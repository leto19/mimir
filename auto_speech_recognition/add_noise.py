import numpy as np
import pyaudio
import math
from scipy.io import wavfile
import matplotlib.pyplot as plt
import sys
def add_white_noise(in_file,SNR=20):
    
    signal_fs,signal = wavfile.read(in_file)
    signal_RMS= math.sqrt(np.mean(signal_fs**2))
    #print(signal_RMS)
    noise_RMS=math.sqrt(signal_RMS**2/(pow(10,SNR/10)))
    noise=np.random.normal(0, noise_RMS, signal.shape[0])
    
    signal_out = signal + noise
    #print(type(signal_out))
    out_file = in_file.replace("test_data2/","wn_data/snr%s/"%SNR)
    print(out_file)
    wavfile.write(out_file,signal_fs,signal_out.astype(np.int16))

def add_pink_noise(in_file,in_noise,SNR=10):
    signal_fs,signal = wavfile.read(in_file)
    signal_RMS= math.sqrt(np.mean(signal_fs**2))
    noise_RMS_desired=math.sqrt(signal_RMS**2/(pow(10,SNR/10)))
    
    noise_fs,noise = wavfile.read(in_noise)
    noise=np.interp(noise, (noise.min(), noise.max()), (-1, 1))
    if(len(noise)>len(signal)):
        noise=noise[0:len(signal)]
    noise_RMS_real = math.sqrt(np.mean(noise**2))

    print(noise_RMS_desired,noise_RMS_real)
    print(noise_RMS_desired/noise_RMS_real)
    noise = noise*(noise_RMS_desired/noise_RMS_real)
   

    signal_out = signal + noise
    #print(type(signal_out))
    out_file = in_file.replace("test_data2/","pn_data/snr%s/"%SNR)
    print(out_file)
    wavfile.write(out_file,signal_fs,signal_out.astype(np.int16))


#add_white_noise(sys.argv[1])    
add_pink_noise(sys.argv[1],"noise_files/pnoise2.wav")