#!/usr/bin/env python3

from vosk import Model, KaldiRecognizer
import sys
import os
import wave
import json
import pyaudio
import numpy
import speech_recognition as sr
#from get_speech_input import noise_reduce
from noise_reduction.noise_reduction import *

model = Model(sys.argv[1])
#model = Model("models/vosk-model-en-us-daanzu-20200905")
#model = Model("models/new")

def get_text(audio_file):
   # pre_emph(audio_file,"emthed.wav")
    #pre_emph("emthed.wav","emthed2.wav")
    #wf = wave.open("emthed.wav", "rb")
    #os.remove("emthed2.wav")
    #os.remove("emthed.wav")
    
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

def get_concept_accuracy(string,concept_list):
    con_counter = 0
    for con in concept_list:
        if con in string:
            con_counter +=1
    print("%s/%s (%s%%)" %(con_counter,len(concept_list),(con_counter/len(concept_list))*100))
    return (con_counter/len(concept_list))*100

model = Model(sys.argv[1])

with open("%s/baseline.txt"%sys.argv[2].split("/")[0]) as f:
    baseline_list = f.readlines()
baseline_index = 0

root = os.curdir + "/"+ sys.argv[2] +"/"
print(root)
#for set_num in range(len(subdirs))
model_name = sys.argv[1].replace("models/","").replace("/","")

for path, subdirs, files in os.walk(root):
    print(subdirs)
    for s in subdirs:
        wer_list = list()
        ca_list = list()
        recog_list = list()
        folder_path = os.path.join(path,s)
        print(folder_path)
        files = os.listdir(folder_path)
        wavs = list()
        for f in files:    
            if f.endswith(".wav"):
               wavs.append(f)
        print(wavs)
        for f in sorted(wavs):
            file_path = os.path.join(folder_path, f)
            print(file_path)
            #noise_reduce(file_path,file_path.replace(".wav","_rn.wav"))
            file_path_nr = file_path.replace(".wav","_rn.wav")
            noise_reduction(file_path,file_path_nr)            
            baseline_text = baseline_list[baseline_index].split("|")[0].strip()
            baseline_concepts = baseline_list[baseline_index].split("|")[1].strip().split(",")
            recognised_text = get_text(file_path_nr)
            os.remove(file_path_nr)
            recognised_text = recognised_text.lower().replace("[noise]","").replace("<unk>","")
            baseline_index+=1
            if baseline_index ==9:
                baseline_index = -1
            recog_list.append(recognised_text)
            wer_list.append(get_WER(baseline_text,recognised_text))
            ca_list.append(get_concept_accuracy(recognised_text,baseline_concepts))

        with open("%s/%s/%s.txt"%(sys.argv[2],s,model_name+"_results") ,"w") as f:
            f.write(model_name +"\n")
            for i in range(len(wer_list)):
                f.write("%s | %s (WER: %s, CA: %s%%) \n"%(baseline_list[i].split("|")[0].strip(),recog_list[i],wer_list[i],ca_list[i]))
            f.write("MEAN WER:" + str(numpy.mean(wer_list))+"\n")
            f.write("MEAN CA:" + str(numpy.mean(ca_list)))
