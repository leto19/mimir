from gtts import gTTS 
from pydub import AudioSegment
from pydub.playback import play
import os
from ctypes import *
from contextlib import contextmanager

ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)

def py_error_handler(filename, line, function, err, fmt):
    pass

c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

@contextmanager
def noalsaerr():
    asound = cdll.LoadLibrary('libasound.so')
    asound.snd_lib_error_set_handler(c_error_handler)
    yield
    asound.snd_lib_error_set_handler(None)

def tts(text):
  with noalsaerr():
    language = 'en'
    yobj = gTTS(text=text, lang=language, slow=False)
    yobj.save("response.mp3")
    res = AudioSegment.from_mp3("response.mp3")
    play(res)
    os.remove("response.mp3")