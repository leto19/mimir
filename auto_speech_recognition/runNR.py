import transplant
import sys
import soundfile as sf
matlab = transplant.Matlab(arguments=['jvm=False'])

matlab.addpath("/home/george/matlab_projects/code_nr_alg3_book/")
matlab.addpath("/home/george/matlab_projects/code_nr_alg3_book/TabGenGam/")


y = matlab.runNR(sys.argv[1])

sf.write(sys.argv[1].replace(".wav","_nr.wav"),y,16000)
