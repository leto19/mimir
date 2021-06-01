import os
import json
import pyaudio
import sys
from ctypes import *
from contextlib import contextmanager
from urllib.parse import urlencode
from pydub import AudioSegment
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import wave 
from vosk import Model, KaldiRecognizer, SetLogLevel
import numpy as np
import noisereduce as nr
from time import sleep
from scipy.io import wavfile
ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
from array import array
from auto_speech_recognition.noise_reduction.noise_reduction import *

class RequestError(Exception): pass

class UnknownValueError(Exception): pass
ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)

def py_error_handler(filename, line, function, err, fmt):
    pass

c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

@contextmanager
def noalsaerr():
    if os.name != 'nt':
        asound = cdll.LoadLibrary('libasound.so')
        asound.snd_lib_error_set_handler(c_error_handler)
        yield
        asound.snd_lib_error_set_handler(None)


def is_silent(data):
    "Returns 'True' if below the 'silent' threshold"
    #print(max(data))
    return max(data) < 500

def get_audio(seconds=3,out_file="auto_speech_recognition/myfile.wav"):
    """returns a wav audio file of audio recorded from the microphone for the specified number of seconds"""
    FS = 16000
    CHUNK = 1024
    SECONDS_RECORD = seconds
    
    with noalsaerr():
        p = pyaudio.PyAudio()

    stream = p.open(format=pyaudio.paInt16, channels=1, rate=FS, input=True, frames_per_buffer=CHUNK)
    frames = []
    
    #get a frame of noise
    data = stream.read(CHUNK)
    frames.append(data)

    num_silent = 0
    snd_started = False

    sleep(0.5)
    print("Listening...")
    for i in range(0, int(FS / CHUNK * SECONDS_RECORD)):
    
        data = stream.read(CHUNK)

        #silence detection adapted from 
        # https://stackoverflow.com/questions/892199/detect-record-audio-in-python
        silent = is_silent(array('h',data))

        if silent and snd_started:
            num_silent += 1
        elif not silent and not snd_started:
            snd_started = True

        if snd_started and num_silent > 30:
            break

        frames.append(data)

    print("Working...")
    stream.stop_stream()
    stream.close() 
    p.terminate()
    wf = wave.open(out_file, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(FS)
    wf.writeframes(b''.join(frames))
    wf.close()
    #reduce noise in file
    #pre_emph(out_file) #do pre empathsis
    #os.rename(out_file.replace(".wav","_preempth.wav"), out_file) #replace old file with pre-emph'd version

def get_speech_input_string_vosk(seconds=10,model=None):
    """returns speech input from the user as a string
    records for the number of seconds specified, default 3"""
    SetLogLevel(-1) #Hides Kaldi outputs to terminal 
    if model == None:
        MODEL_PATH = "auto_speech_recognition/models/all3"
        model = Model("%s"%os.environ["MIMIR_DIR"]+MODEL_PATH)

    get_audio(seconds)
    #noise_reduce(in_file="auto_speech_recognition/myfile.wav",out_file="auto_speech_recognition/myfile_nr.wav") 
    noise_reduction("auto_speech_recognition/myfile.wav", "auto_speech_recognition/myfile_nr.wav")
    wf = wave.open("auto_speech_recognition/myfile_nr.wav", 'rb')
    data = wf.readframes(10000000) # Hmm
    os.remove("auto_speech_recognition/myfile.wav")
    os.remove("auto_speech_recognition/myfile_nr.wav")

    rec = KaldiRecognizer(model, 16000) 
    if rec.AcceptWaveform(data):
        res = json.loads(rec.FinalResult())
        #print(rec)
        #print(res)
        #print(res['text'])
        return res['text'].lower().replace("[noise]","")
    else:
        print("Didn't hear anything...")
        return "NONE"


def get_speech_input_string_google(file_name="auto_speech_recognition/myfile.flac",language="en-GB",show_all=True,keep_files=False):
    #the following is adapted from speech_recognition module    
        get_audio(10)
        noise_reduction("auto_speech_recognition/myfile.wav", "auto_speech_recognition/myfile.wav")
        sound = AudioSegment.from_wav("auto_speech_recognition/myfile.wav") #convert to flac 
        sound.export("auto_speech_recognition/myfile.flac",format = "flac")
        if not keep_files: 
            os.remove("auto_speech_recognition/myfile.wav")
        with open(file_name,"rb") as f:
            audio_data = f.read()
        if not keep_files: os.remove(file_name)        
        #key = "AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw"
        key="AIzaSyBx_4G98LdFhnapUfA3tAmqqPGWGNpAawM"
        url = "http://www.google.com/speech-api/v2/recognize?{}".format(urlencode({
            "client": "chromium",
            "lang": language,
            "key": key,
            "app": "mimir"
        }))
        request = Request(url, data=audio_data, headers={"Content-Type": "audio/x-flac; rate={}".format(16000)})
        #response = urlopen(request)
        try:
            response = urlopen(request)
        except HTTPError as e:
            raise RequestError("recognition request failed: {}".format(e.reason))
        except URLError as e:
            raise RequestError("recognition connection failed: {}".format(e.reason))

        response_text = response.read().decode("utf-8")
        #print("responce text:\n",response_text)
        # ignore any blank blocks
        actual_result = []
        for line in response_text.split("\n"):
            if not line: continue
            result = json.loads(line)["result"]
            if len(result) != 0:
                actual_result = result[0]
                break
        if len(result) == 0:
            return '{"alternative":[{"transcript":"ERROR","confidence":0.0}]}'
        json_result = json.dumps(result[0])
        #print("JSON RESULT:\n",json_result,type(json_result))
        if show_all: return json_result
        """
        if "confidence" in actual_result["alternative"]:
            # return alternative with highest confidence score
            best_hypothesis = max(actual_result["alternative"], key=lambda alternative: alternative["confidence"])
        else:
            # when there is no confidence available, we arbitrarily choose the first hypothesis.
            best_hypothesis = actual_result["alternative"][0]
        if "transcript" not in best_hypothesis: raise "what did you say?"
        return best_hypothesis["transcript"]
        """


## SIGNAL PROCESSING 
"""
def noise_reduce(in_file="auto_speech_recognition/myfile.wav",out_file="auto_speech_recognition/myfile.wav"):
    fs, data = wavfile.read(in_file) # read in the file data 
    data = data.astype(np.float32, order='C') / 32768.0 #convert to 32bit float
    noisy_part = data[0:2048] #get the noisy section
    reduced_noise = nr.reduce_noise(audio_clip=data, noise_clip=noisy_part)
    reduced_noise = (reduced_noise* 32767).astype(np.int16, order='C') #convert back 16 bit int
    #reduced_noise = reduced_noise[2048:] #trim the start 
    wavfile.write(out_file,fs,reduced_noise) 

def pre_emph(in_file,out_file=""):
    if out_file == "":
        out_file = in_file.replace(".wav","_preempth.wav")

    s = aubio.source(in_file)
    Fs = s.samplerate

    filt = aubio.digital_filter(3)
    z1 = -np.exp(-1.0/(Fs*0.000075))
    p1 = 1 +z1
    
    a1 = p1
    a2 = 0
    b0 = 1.0
    b1 = z1
    b2 = 1.0

    filt.set_biquad(-1.700724,0.7029382,0.2380952,-0.1718791,-0.0442981) #magic numbers do not touch
    
    #filt.set_biquad(1.0,0847423215,0.73908439754585875,0.93117565229670540,0.0)
    #filt.set_biquad(1,-1.700724,0.7029382,-0.7218922,-0.1860521) #magic numbers do not touch
    #filt.set_biquad(b0,b1,b2,a1,a2) #magic numbers do not touch
    #filt.set_biquad(0.2513790015131591,0.5027580030263182,0.251379001.992894625131591,-0.17124071441396285,0.1767567204665992) #magic numbers do not touch
    
    out = aubio.sink(out_file,Fs)

    total_frames = 0
    while True:
        samples, read = s()
        # filter samples
        filtered_samples = filt(samples)
        # write to sink
        out(filtered_samples, read)
        # count frames read
        total_frames += read
        # end of file reached
        if read < s.hop_size:
            break
"""

if __name__ == "__main__":
    #j = json.loads(get_speech_input_string_google(keep_files=True))
    
    #print(j["alternative"][0]["transcript"])

    print(get_speech_input_string_vosk())
