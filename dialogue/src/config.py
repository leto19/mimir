from .utils import embedding_cos_sim, is_question
import dialogue.src.context as context
from enum import Enum

# Dialogue Options Enum
class DialogueOption(Enum):
  EXIT = 0               # exit system  
  DA_RESPONSE = 1        # response from the dialogue system
  QA_RESPONSE = 2        # get response from the qa system
  #QA_MT_RESPONSE = 4    # multi-turn qa response
  BOOK_CONFIRMED = 3     # response from dialogue system + book confirmation

# States Enum
class States(Enum):
  ANY = 'ANY'
  ENTRY = "ENTRY"
  CONFIRM_BOOK = "CONFIRM BOOK"
  NEUTRAL = "NEUTRAL"
  CLARIFY = "CLARIFY"
  ANSWER = "ANSWER"
  END = "END"

# Transition class
class Transition():
  def __init__(self, 
      src_state,                   # Enum: State
      dst_state,                   # Enum: State 
      dialogue_option,             # Enum: DialogueOption
      condition=True,              # Bool OR Function (returns Bool)
      response=""):                # String OR Function (returns String)
    self.src = src_state
    self.dst = dst_state
    self.dialogue_id = dialogue_option
    self.cond = condition
    self.res = response

  def __str__(self):
    return "[{} -> {}]".format(self.src, self.dst)

  def condition(self, utterance):
    return self.cond if isinstance(self.cond, bool) else self.cond(utterance)

  def response(self):
    return self.res if isinstance(self.res, str) else self.res()


# The lower threshold for the cosine similarity calculations
SIM_THRESHOLD = 0.7

# Standard Transitions
STATE_TRANSITIONS = [
  Transition(        
    States.ENTRY,
    States.CONFIRM_BOOK,
    DialogueOption.DA_RESPONSE,
    lambda x: context.is_book_present(x),
    context.suggest_book
  ),
  Transition(        
    States.ENTRY,
    States.ENTRY,
    DialogueOption.DA_RESPONSE,
    lambda x: not context.is_book_present(x),
    "I'm sorry, I cannot find the book you're looking for, it may not be currently supported. " + 
    "Is there another book you'd like to try?"
  ),
  Transition(        
    States.CONFIRM_BOOK,
    States.CONFIRM_BOOK,
    DialogueOption.DA_RESPONSE,
    lambda x: (
      embedding_cos_sim(x, "no") > SIM_THRESHOLD 
      and context.is_suggested_book()
    ),
    lambda: context.suggest_book()
  ),
  Transition(        
    States.CONFIRM_BOOK,
    States.ENTRY,
    DialogueOption.DA_RESPONSE,
    lambda x: (
      embedding_cos_sim(x, "no") > SIM_THRESHOLD
      and not context.is_suggested_book()
    ),
    "I'm sorry, I cannot find the book you're looking for, it may not be currently supported. " + 
    "Is there another book you'd like to try?"  
  ),
  Transition(        
    States.CONFIRM_BOOK,
    States.NEUTRAL,
    DialogueOption.BOOK_CONFIRMED,
    lambda x: embedding_cos_sim(x, "yes") > SIM_THRESHOLD,
    lambda: context.confirm_book()
  ),
  Transition(        
    States.NEUTRAL,
    States.ANSWER,
    DialogueOption.QA_RESPONSE,
    lambda x: is_question(x.lower()),    
  ),
  Transition(        
    States.ANSWER,
    States.ANSWER,
    DialogueOption.QA_RESPONSE,
    lambda x: is_question(x.lower()),    
  ),
  Transition(        
    States.ANSWER,
    States.NEUTRAL,
    DialogueOption.DA_RESPONSE,
    lambda x: embedding_cos_sim(x, "okay great") > SIM_THRESHOLD,
    "Let me know if you have another question."
  ),
  Transition(        
    States.NEUTRAL,
    States.NEUTRAL,
    DialogueOption.DA_RESPONSE,
    lambda x: embedding_cos_sim(x, "okay great") > SIM_THRESHOLD,
    ""
  )
]

# Special Transitions
EXIT_TRANSITION = Transition(
    States.ANY,
    States.END,
    DialogueOption.EXIT,
    lambda x: embedding_cos_sim(x, "exit") > SIM_THRESHOLD,
    "Goodbye."
)

ENTRY_TRANSITION = Transition(
    None,
    States.ENTRY,
    DialogueOption.DA_RESPONSE,
    True,
    "Hello, what book are you reading today?"
)

# All Transitions
TRANSITIONS = [
  ENTRY_TRANSITION,
  *STATE_TRANSITIONS,
  EXIT_TRANSITION,
]