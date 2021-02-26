import numpy as np
from . algorithm import algorithm
import soundfile as sf

def noise_reduction(in_file,out_file):

    parameters = dict()
    parameters['fs'] = 16000
    parameters['min_gain'] = 10**(-20/20)
    parameters['alpha'] = 0.99
    parameters['frLen'] = int(32e-3*parameters['fs'])
    parameters['fShift'] = int(parameters['frLen']/2)
    parameters['anWin'] = np.sqrt(np.hanning(parameters['frLen']))
    parameters['synWin'] = np.sqrt(np.hanning(parameters['frLen']))
    parameters['snr_low_lim'] = 2.2204e-16
    s,fs = sf.read(in_file)
    y = s
    # gamma = 1
    # nu = 0.6
    # g_dft, g_mag, g_mag2 = tabulate_gain_functions(gamma, nu)
    g_mag = np.load("auto_speech_recognition/noise_reduction/gain.npy")
    parameters['g_mag'] = g_mag
    shat = algorithm(y, parameters)
    #shat = float2pcm(shat)
    #wavfile.write("out.wav",fs,shat)
    sf.write(out_file,shat,fs)
    #print("done!")

if __name__ == '__main__':
    import sys
    noise_reduction(sys.argv[1], sys.argv[2])
