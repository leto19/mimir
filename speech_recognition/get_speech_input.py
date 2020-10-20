#!/usr/bin/env python3

from vosk import Model, KaldiRecognizer
import os
import json
import pyaudio
import sys
import wave
#model = Model("models/vosk-model-en-us-daanzu-20200905")

def get_audio():
    RATE = 16000
    FRAMES = 8000
    CHUNK = 100
    SECONDS_RECORD = 3
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=FRAMES)
    frames = []
    os.system('clear')
    input("press enter to continue:")
    print("Listening...")
    for i in range(0, int(RATE / CHUNK * SECONDS_RECORD)):
        data = stream.read(CHUNK)
        frames.append(data)
        print

    stream.stop_stream()
    stream.close()
    p.terminate()
    return b''.join(frames)


model = Model("%s"%sys.argv[1])
rec = KaldiRecognizer(model, 16000)

if rec.AcceptWaveform(get_audio()):
    res = json.loads(rec.FinalResult())
    print(res['text'])
else:
    print("Didn't hear anything...")
#res = json.loads(rec.FinalResult())
#print(res['text'])

