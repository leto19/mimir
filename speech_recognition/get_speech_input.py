#!/usr/bin/env python3

from vosk import Model, KaldiRecognizer, SetLogLevel
import os
import json
import pyaudio
import sys
from ctypes import *
from contextlib import contextmanager

ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)

def py_error_handler(filename, line, function, err, fmt):
    pass

c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

@contextmanager
def noalsaerr():
    asound = cdll.LoadLibrary('libasound.so')
    asound.snd_lib_error_set_handler(c_error_handler)
    yield
    asound.snd_lib_error_set_handler(None)

def get_audio(seconds=3):
    """returns a audio stream from the microphone for the specified number of seconds"""
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
    return b''.join(frames)



def get_speech_input_string(seconds=5):
    """returns speech input from the user as a string
    records for the number of seconds specified, default 3"""
    SetLogLevel(-1) #Hides Kaldi outputs to terminal 
    MODEL_PATH = "speech_recognition/live_models/tdnn_1d_sp_chain_online"
    model = Model("%s"%os.environ["MIMIR_DIR"]+MODEL_PATH)
    rec = KaldiRecognizer(model, 16000)
    if rec.AcceptWaveform(get_audio(seconds)):
        res = json.loads(rec.FinalResult())
        #print(rec)
        #print(res)
        #print(res['text'])
        return res['text'].lower()
    else:
        print("Didn't hear anything...")
        return "NONE"
    

if __name__ == "__main__":
    get_speech_input_string()