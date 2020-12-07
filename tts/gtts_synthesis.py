from gtts import gTTS 
from pydub import AudioSegment
from pydub.playback import play
import os


def tts(text):
  language = 'en'
  yobj = gTTS(text=text, lang=language, slow=False)
  yobj.save("response.mp3")
  res = AudioSegment.from_mp3("response.mp3")
  play(res)
  os.remove("response.mp3")
