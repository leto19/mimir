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
import numpy as np
import noisereduce as nr
from time import sleep
from scipy.io import wavfile
ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
from array import array
class RequestError(Exception): pass

class UnknownValueError(Exception): pass

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

def get_audio(seconds=3):
    """returns a flac audio file of audio recorded from the microphone for the specified number of seconds"""
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
    wf = wave.open("auto_speech_recognition/myfile.wav", 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(FS)
    wf.writeframes(b''.join(frames))
    wf.close()
    noise_reduce()
    sound = AudioSegment.from_wav("auto_speech_recognition/myfile.wav")
    sound.export("auto_speech_recognition/myfile.flac",format = "flac")

def get_speech_input_string_google(file_name="auto_speech_recognition/myfile.flac",language="en-GB",show_all=True,keep_files=False):
    #the following is adapted from speech_recognition module    
        get_audio(10)
        if not keep_files: os.remove("auto_speech_recognition/myfile.wav")

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
        json_result = json.dumps(result[0])
        print("JSON RESULT:\n",json_result,type(json_result))
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

def noise_reduce(in_file="auto_speech_recognition/myfile.wav",out_file="auto_speech_recognition/myfile.wav"):
    fs, data = wavfile.read(in_file)
    data = data.astype(np.float32, order='C') / 32768.0 #convert to 32bit float
    
    noisy_part = data[0:2048] #get the noisy section

    reduced_noise = nr.reduce_noise(audio_clip=data, noise_clip=noisy_part)

    reduced_noise = (reduced_noise* 32767).astype(np.int16) #convert back 16 bit int
    reduced_noise = reduced_noise[2048:] #trim the start 
    wavfile.write(out_file,fs,reduced_noise) 





if __name__ == "__main__":
    j = json.loads(get_speech_input_string_google(keep_files=False))
    print(j["alternative"][0]["transcript"])

