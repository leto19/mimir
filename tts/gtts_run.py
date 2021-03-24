from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import os
from ctypes import *
from contextlib import contextmanager
import soundfile as sf
ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)

def py_error_handler(filename, line, function, err, fmt):
    pass

c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

@contextmanager
def noalsaerr():
  if os.name == 'nt': return
  asound = cdll.LoadLibrary('libasound.so')
  asound.snd_lib_error_set_handler(c_error_handler)
  yield
  asound.snd_lib_error_set_handler(None)

def add_effect(in_file,out_file):
  from pysndfx import AudioEffectsChain

  fx = (
      AudioEffectsChain()
      #.highshelf()
      .phaser()
      #.delay(0.4,0.6,[0.5,0.25])
      #.overdrive(gain=5,colour=4)
      .pitch(-300,use_tree=True)
      .reverb(reverberance=5)
      .speed(1.1)
      #.bend([["0","180",".25"],["0","90","1"],["0","10",".25"]])
      .lowshelf(gain=-20.0,frequency=250,slope=0.8)
      .tremolo(90,50)
      .equalizer(20)
      .custom("chorus 1 .5 100 0.8 1 3 -s")
      .custom("synth sine fmod 10 echo 0.8 0.8 29 0.8")
  )

  fx(in_file,out_file)
  #y,fs = sf.read(in_file)
  #print(type(y))
  
def tts(text):
  with noalsaerr():
    language = 'en'
    yobj = gTTS(text=text,tld="co.uk", lang=language, slow=False)
    yobj.save("response.mp3")
    


    res = AudioSegment.from_mp3("response.mp3")
    res.export("response.wav",format="wav")
    os.remove("response.mp3")
    add_effect("response.wav","response_e.wav")
    res = AudioSegment.from_file("response_e.wav")
    os.remove("response.wav")
    os.remove("response_e.wav")
    play(res)





if __name__ == "__main__":
  import sys
  tts(sys.argv[1])