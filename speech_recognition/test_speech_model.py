#!/usr/bin/env python3

from vosk import Model, KaldiRecognizer
import sys
import os
import wave
import json
import pyaudio
import numpy




model = Model(sys.argv[1])
#model = Model("models/vosk-model-en-us-daanzu-20200905")
#model = Model("models/new")

def get_text(audio_file):
    wf = wave.open(audio_file, "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        print ("Audio file must be WAV format mono PCM.")
        exit (1)
    rec = KaldiRecognizer(model, wf.getframerate())

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            pass
            #print(rec.Result())
        else:
            pass
            #print(rec.PartialResult())
    #print(rec.FinalResult())
    res = json.loads(rec.FinalResult())
    #os.system('clear')
    return (res['text'])


def get_WER(r,h):
    """
    Adapted from:
    https://github.com/imalic3/python-word-error-rate
    """

    d = numpy.zeros((len(r) + 1) * (len(h) + 1), dtype=numpy.uint16)
    d = d.reshape((len(r) + 1, len(h) + 1))
    for i in range(len(r) + 1):
        for j in range(len(h) + 1):
            if i == 0:
                d[0][j] = j
            elif j == 0:
                d[i][0] = i

    for i in range(1, len(r) + 1):
        for j in range(1, len(h) + 1):
            if r[i - 1] == h[j - 1]:
                d[i][j] = d[i - 1][j - 1]
            else:
                substitution = d[i - 1][j - 1] + 1
                insertion = d[i][j - 1] + 1
                deletion = d[i - 1][j] + 1
                d[i][j] = min(substitution, insertion, deletion)
    result = float(d[len(r)][len(h)]) / len(r) * 100

    print(r,"|", h)
    print("WER:",result)
    return result


model = Model(sys.argv[1])

with open("test_data/baseline.txt") as f:
    baseline_list = f.readlines()
baseline_index = 0

root = os.curdir + "/test_data/"
#for set_num in range(len(subdirs))
model_name = sys.argv[1].replace("models/","").replace("/","")

for path, subdirs, files in os.walk(root):
    for s in subdirs:
        wer_list = list()
        recog_list = list()
        folder_path = os.path.join(path,s)
        print(folder_path)
        files = os.listdir(folder_path)
        for f in files:
            if ".wav" not in f:
                files.remove(f)
        for f in sorted(files):
            file_path = os.path.join(folder_path, f)
            print(file_path)

            baseline_text = baseline_list[baseline_index].strip()
            recognised_text = get_text(file_path)
            baseline_index+=1
            recog_list.append(recognised_text)
            wer_list.append(get_WER(baseline_text,recognised_text))

        with open("test_data/%s/%s.txt"%(s,model_name+"_results") ,"w") as f:
            f.write(model_name +"\n")
            for i in range(len(wer_list)):
                f.write("%s | %s (WER: %s) \n"%(baseline_list[i].strip(),recog_list[i],wer_list[i]))

