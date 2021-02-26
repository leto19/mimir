from .src import StateMachine, States, TRANSITIONS, DialogueOption, get_confirmed_book
from .models import QuestionClassifier

global DSM
global QUEST_CLS

def init_dialogue():
  '''Initialise a dialogue state machine'''
  global DSM
  DSM = StateMachine(States, TRANSITIONS, States.ENTRY, States.ANY)

  global QUEST_CLS
  QUEST_CLS = QuestionClassifier()

  transition = DSM.init_trans()

  return {
    "id": transition.dialogue_id,
    "response": transition.response(),
  }


def dialogue_input(user_utterance):
  '''Given a user input (text), return the dialogue option 
     plus necessary information'''
  global DSM
  transition = DSM.process_input(user_utterance)
  
  question_cls = None
  # If the input is a question, classify the question
  if (transition.dialogue_id == DialogueOption.QA_RESPONSE):
    question_cls = QUEST_CLS.classify(user_utterance) 
    print("QUESTION CLASS: {}".format(question_cls))

  retDict = {
    "id": transition.dialogue_id,
    "response": transition.response(),
    "cls": question_cls,
  }

  if (transition.dialogue_id == DialogueOption.BOOK_CONFIRMED):
    retDict['book'] = get_confirmed_book()

  return retDict