#!/usr/bin/env python3

from vosk import Model, KaldiRecognizer
import os
import json
import pyaudio
import sys
#model = Model("models/vosk-model-en-us-daanzu-20200905")
model = Model("%s"%sys.argv[1])
rec = KaldiRecognizer(model, 8000)

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=8000, input=True, frames_per_buffer=8000)
stream.start_stream()

while True:
    data = stream.read(4000)
    if len(data) == 0:
        break
    if rec.AcceptWaveform(data):
        print(rec.Result())
    else:
        print(rec.PartialResult())

#print(rec.FinalResult())
res = json.loads(rec.FinalResult())
print(res['text'])