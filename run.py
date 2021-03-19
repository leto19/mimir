import os
os.environ["MIMIR_DIR"] = "./"
import argparse
#import speech_recognition.get_speech_input as sr
from dialogue import init_dialogue, dialogue_input, DialogueOption, bold_print
from qa.question_answering.question_classifiers import QuestionClassifier
#from qa.corpus_utils import ner_pipeline
#from qa.corpus_utils.ner_pipeline import *
from qa.question_answering.models.model import ModelController
import json


parser = argparse.ArgumentParser()
parser.add_argument("-v","--verbose", action="store_true") #Run in verbose mode to view 
				#which model answers user questions
parser.add_argument("-s","--silent", action="store_true") #No TTS or ASR

args = parser.parse_args()

if not args.silent:
    from tts.gtts import tts
    import auto_speech_recognition.get_speech_input as asrg
    from vosk import Model
    print("loading asr model...")
    asr_model = Model("%s"%os.environ["MIMIR_DIR"]+"models/all")

class NaturalLanguageGenerator():
	"""A placeholder Natural Language Generation class. We should figure out
		a better place to put this """
	def generate(self, answer_type, answer):
		if answer == None:
			generated_string = "Sorry, I couldn't find the answer"
		if answer_type == "CHARLIST":
			generated_string = "The main characters are {} and {}".format(", ".join(answer[:-1]),answer[-1])
		else:
			generated_string = str(answer)
		return(generated_string)
os.system('play -nq -t alsa synth 0.5 sine 293.66')
os.system('play -nq -t alsa synth 0.7 sine 261.63')
if __name__ == '__main__':

  persist_dialogue = True
  # Initialise dialogue + other components
  ret = init_dialogue()
  qc = QuestionClassifier()
  mc = ModelController(verbose=args.verbose)
  nlg = NaturalLanguageGenerator()
  os.system('clear')
  bold_print(ret["response"])
  if not args.silent:
    tts(ret["response"])

  # While not in end_state, keep running
  while persist_dialogue:

    user_input = input("(Press Enter for ASR)\n> ")
    if user_input == "" and not args.silent: # if the user dosn't type a question, use ASR
      """
      j = json.loads(asrg.get_speech_input_string_vosk())
      #this json object contains the best result in "alternative"
      #with the actual text being "transcript" and the confidence % "confidence"
      if "confidence" in j["alternative"][0]: 
        conf = float(j["alternative"][0]["confidence"])*100 #formatting
      else:
        conf = "???"# sanity :-) 
      user_input = j["alternative"][0]["transcript"]
      print("You said: '%s' (%s%%):"%(user_input,conf))

      """
      os.system('play -nq -t alsa synth 0.5 sine 293.66')
      user_input = asrg.get_speech_input_string_vosk(model=asr_model)
      os.system('play -nq -t alsa synth 0.7 sine 261.63')
      print("You said: '%s'"%(user_input))

      #log_inputs(user_input,"s")
    #else:
      #log_inputs(user_input,"t")
    # pass user input to dialogue, which returns a response and/or a code signifying QA comp is needed (or user has chosen to exit)
    
    ret = dialogue_input(user_input)
    dialogue_id = ret['id']

    response = None 

    if dialogue_id == DialogueOption.EXIT:
      response = ret['response']

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
      response = mc.answer_question(user_input) #Model selection procedure now implemented inside mc.answer_question
    # use TTS component to read response out
    if not args.silent:
      tts(response)

    bold_print(response)

