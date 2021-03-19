from .src import StateMachine, States, TRANSITIONS, DialogueOption, get_confirmed_book
from .models import QuestionClassifier

global DSM

def init_dialogue():
  '''Initialise a dialogue state machine'''
  global DSM
  DSM = StateMachine(States, TRANSITIONS, States.ENTRY, States.ANY)


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
  
  retDict = {
    "id": transition.dialogue_id,
    "response": transition.response(),
  }

  if (transition.dialogue_id == DialogueOption.BOOK_CONFIRMED):
    retDict['book'] = get_confirmed_book()

  return retDict