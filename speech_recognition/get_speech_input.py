#!/usr/bin/env python3

from vosk import Model, KaldiRecognizer, SetLogLevel
import os
import json
import pyaudio
import sys

#model = Model("models/vosk-model-en-us-daanzu-20200905")

def get_audio(seconds=3):
    """returns a audio stream from the microphone for the specified number of seconds"""
    FS = 16000
    CHUNK = 1024
    SECONDS_RECORD = seconds
    p = pyaudio.PyAudio()

    stream = p.open(format=pyaudio.paInt16, channels=1, rate=FS, input=True, frames_per_buffer=CHUNK)
    frames = []
    os.system('clear')
    input("press enter to continue:")
    print("Listening...")
    for i in range(0, int(FS / CHUNK * SECONDS_RECORD)):
        data = stream.read(CHUNK)
        frames.append(data)
        print(i)

    stream.stop_stream()
    stream.close() 
    p.terminate()
    return b''.join(frames)



def get_input_string(seconds=5):
    """returns speech input from the user as a string
    records for the number of seconds specified, default 3"""
    SetLogLevel(-1) #Hides Kaldi outputs to terminal 
    model = Model("%s"%sys.argv[1])
    rec = KaldiRecognizer(model, 16000)
    if rec.AcceptWaveform(get_audio(seconds)):
        res = json.loads(rec.FinalResult())
        print(rec)
        print(res)
        print(res['text'])
        return res['text']
    else:
        print("Didn't hear anything...")
        return ""
    

if __name__ == "__main__":
    get_input_string()