from vosk import Model, KaldiRecognizer, SetLogLevel
import subprocess
import pyaudio
from ctypes import *
from contextlib import contextmanager
import json
import os
from array import array
ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
import wave
import mimir_hf
import gc
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
        
def listen():

    FS = 16000
    CHUNK = 1024
    SECONDS_RECORD = 3
    model = Model("auto_speech_recognition/models/wake")
    os.system('clear')
    with noalsaerr():
        p = pyaudio.PyAudio()

    stream = p.open(format=pyaudio.paInt16, channels=1, rate=FS, input=True, frames_per_buffer=CHUNK)
    frames = []
    
    #get a frame of noise
    data = stream.read(CHUNK)
    frames.append(data)

    num_silent = 0
    snd_started = False
    text = ""
    #sleep(0.5)
    print("Listening for wake word 'mimir'")
    while "mimir" not in text.split(): #TODO fix this 
        text = ""
        num_silent = 0
        snd_started = False
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

        #print("Working...")
        
        wf = wave.open("listen.wav", 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(FS)
        wf.writeframes(b''.join(frames))
        wf.close()
        text = recognise("listen.wav",model)
        os.remove("listen.wav")

        #print(text)
    # if the wake word is spoken:
    stream.stop_stream()
    stream.close() 
    p.terminate()
     #a little hacky but  it works 
    
    mimir_hf.run()
    print("going back to wake word mode...")
    listen()
    gc.collect()
def recognise(in_audio,model):
    SetLogLevel(-1) #Hides Kaldi outputs to terminal 

    wf = wave.open(in_audio, 'rb')
    data = wf.readframes(10000000) # Hmm
    rec = KaldiRecognizer(model, 16000)
    if rec.AcceptWaveform(data):
        res = json.loads(rec.FinalResult())
        #print(rec)
        #print(res)
        #print(res['text'])
        return res['text'].lower().replace("[noise]","")
    else:
        #print("Didn't hear anything...")
        return "NONE"

if __name__ == '__main__':
    listen()