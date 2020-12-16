#import speech_recognition.get_speech_input as sr
from dialogue import init_dialogue, dialogue_input, DialogueOption, bold_print
from tts.gtts import tts
from qa.question_answering.models.model import ModelController
import auto_speech_recognition.get_speech_input as asr
import os

if __name__ == '__main__':

  persist_dialogue = True
  # Initialise dialogue + other components
  ret = init_dialogue()
  mc = ModelController()
  os.system('clear')
  bold_print(ret["response"])
  tts(ret["response"])

  # While not in end_state, keep running
  while persist_dialogue:

    #user_input = sr.get_input_string() # returns string
    user_input = input("(Press Enter↩ for ASR)\n> ")
    if user_input == "": # if the user dosn't type a question, use ASR
      user_input = asr.get_speech_input_string_google() # requires speech_recognition module
      print("You said:",user_input)
    # pass user input to dialogue, which returns a response and/or a code signifying QA comp is needed (or user has chosen to exit)
    ret = dialogue_input(user_input)
    dialogue_id = ret['id']

    response = None 

    if dialogue_id == DialogueOption.EXIT:
      persist_dialogue = False

    elif dialogue_id == DialogueOption.DA_RESPONSE:
      response = ret['response']

    elif dialogue_id == DialogueOption.BOOK_CONFIRMED:
      book_title = ret['book'] # pass to qa
      mc.confirm_book(book_title)
      response = ret['response']


    elif dialogue_id == DialogueOption.QA_RESPONSE:
      # if QA comp is needed, get response from QA system
      #response = "*Answer*" # get from QA component
      response = mc.answer_question('bert_baseline_summary',user_input)
      #response = mc.answer_question('cosine_distance_tfidf_fulltext', user_input)

    # use TTS component to read response out
    tts(response)

    bold_print(response)

