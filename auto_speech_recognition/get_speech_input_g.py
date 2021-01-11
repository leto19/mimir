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

ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
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

def get_audio(seconds=3):
    """returns a flac audio file of audio recorded from the microphone for the specified number of seconds"""
    FS = 16000
    CHUNK = 1024
    SECONDS_RECORD = seconds
    with noalsaerr():
        p = pyaudio.PyAudio()

    stream = p.open(format=pyaudio.paInt16, channels=1, rate=FS, input=True, frames_per_buffer=CHUNK)
    frames = []
    #os.system('clear')
    #input("press enter to continue:")
    print("Listening...")
    for i in range(0, int(FS / CHUNK * SECONDS_RECORD)):
        data = stream.read(CHUNK)
        frames.append(data)
        #print(i)

    stream.stop_stream()
    stream.close() 
    p.terminate()
    wf = wave.open("auto_speech_recognition/myfile.wav", 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(FS)
    wf.writeframes(b''.join(frames))
    wf.close()
    sound = AudioSegment.from_wav("auto_speech_recognition/myfile.wav")
    sound.export("auto_speech_recognition/myfile.flac",format = "flac")
    os.remove("auto_speech_recognition/myfile.wav")

def get_speech_input_string_google(file_name="auto_speech_recognition/myfile.flac",language="en-GB",show_all=True):
    #the following is adapted from speech_recognition module    
        get_audio(5)
        with open(file_name,"rb") as f:
            audio_data = f.read()
        os.remove(file_name)        
        #key = "AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw"
        key="AIzaSyBx_4G98LdFhnapUfA3tAmqqPGWGNpAawM"
        url = "http://www.google.com/speech-api/v2/recognize?{}".format(urlencode({
            "client": "chromium",
            "lang": language,
            "key": key,
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

if __name__ == "__main__":
    j = json.loads(get_speech_input_string_google())
    print(j["alternative"][0]["transcript"])

