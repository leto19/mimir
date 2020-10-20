#!/usr/bin/env python3

from vosk import Model, KaldiRecognizer
import sys
import os
import wave
import json
wf = wave.open(sys.argv[1], "rb")
if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
    print ("Audio file must be WAV format mono PCM.")
    exit (1)

#model = Model("models/vosk-model-small-en-us-0.4")
#model = Model("models/vosk-model-en-us-daanzu-20200905")
model = Model("models/new")

# You can also specify the possible word or phrase list as JSON list, the order doesn't have to be strict
rec = KaldiRecognizer(model, wf.getframerate())

#os.system('clear')

while True:
    data = wf.readframes(4000)
    if len(data) == 0:
        break
    if rec.AcceptWaveform(data):
        pass
        print(rec.Result())
    else:
        pass
        print(rec.PartialResult())

print(rec.FinalResult())
res = json.loads(rec.FinalResult())
print(res['text'])