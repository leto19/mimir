from utils import embedding_cos_sim, is_question
import context


# States
S_START = "STATE: START"
S_CONFIRM_BOOK = "STATE: CONFIRM BOOK" 
S_NEUTRAL = "STATE: NEUTRAL"
S_CLARIFY = "STATE: CLARIFY" # State for filling in missing info from a question
S_ANSWER = "STATE: ANSWER"
S_END = "STATE: END"

STATES = [S_START, S_NEUTRAL, S_CLARIFY, S_ANSWER, S_END]

# The lower threshold for the cosine similarity calculations
SIM_THRESHOLD = 0.6

# Maybe create class for this later?
TRANSITIONS = (
  # {
  #   'src':, 
  #   'dst':, 
  #   'condition':, 
  #   'response': 
  # }
  {
    'src': S_START,
    'dst': S_CLARIFY,
    'condition': lambda x: context.is_book_present(x),
    'response': lambda: context.suggest_book()
  },
  {
    'src': S_START,
    'dst': S_START,
    'condition': lambda x: True,
    'response': lambda: (
      "I'm sorry, I cannot find the book you're looking for. " +
      "Is there another book you'd like to try?"
    )
  },
  {
    'src': S_CLARIFY,
    'dst': S_CLARIFY,
    'condition': lambda x: (
      embedding_cos_sim(x, "no") > SIM_THRESHOLD # and is not final suggestion_
      and context.is_suggested_book()
    ),
    'response': lambda: context.suggest_book()
  },
  {
    'src': S_CLARIFY,
    'dst': S_START,
    'condition': lambda x: (
      embedding_cos_sim(x, "no") > SIM_THRESHOLD
      and not context.is_suggested_book()
    ),
    'response': lambda: (
      "I'm sorry, I cannot find the book you're looking for. " +
      "Is there another book you'd like to try?"
    )
  },
  {
    'src': S_CLARIFY,
    'dst': S_NEUTRAL,
    'condition': lambda x: embedding_cos_sim(x, "yes") > SIM_THRESHOLD, # This is going to have to become a probability to allow for compariso
    'response': lambda: context.confirm_book()
  },
  {
    'src': S_NEUTRAL,
    'dst': S_ANSWER,
    'condition': lambda x: is_question(x),
    'response': lambda: "This is the answer to your question"
  },
  {
    'src': S_ANSWER,
    'dst': S_ANSWER,
    'condition': lambda x: is_question(x),
    'response': lambda: "This is the answer to your other question"
  },
  {
    'src': S_ANSWER,
    'dst': S_NEUTRAL,
    'condition': lambda x: embedding_cos_sim(x, "okay great") > SIM_THRESHOLD,
    'response': lambda: "Is there anything else I can you help you with?"
  },
  {
    'src': S_NEUTRAL,
    'dst': S_NEUTRAL,
    'condition': lambda x: embedding_cos_sim(x, "yes") > SIM_THRESHOLD,
    'response': lambda: "What is it?"
  },
  {
    'src': S_NEUTRAL,
    'dst': S_END,
    'condition': lambda x: embedding_cos_sim(x, "no") > SIM_THRESHOLD,
    'response': "Okay, goodbye."
  },
)