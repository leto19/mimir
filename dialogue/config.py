import re
from utils import embedding_cos_sim

# States
S_START = "STATE: START" 
S_ANSWER = "STATE: ANSWER"
S_NEUTRAL = "STATE: NEUTRAL"
S_END = "STATE: END"

STATES = [S_START, S_ANSWER, S_NEUTRAL, S_END]

# Maybe create class for this later
TRANSITIONS = (
  # {
  #   'src':, 
  #   'dst':, 
  #   'condition':, 
  #   'response': 
  # }
  {
    'src': S_START,
    'dst': S_ANSWER,
    'condition': lambda x: re.match("(who|what|where|when|how|why|whose|who's)", x),
    'response': "This is the answer to your question"
  },  
  {
    'src': S_ANSWER,
    'dst': S_NEUTRAL,
    'condition': lambda x: embedding_cos_sim(x, "okay great") > 0.7,
    'response': "Is there anything else I can you help you with?"
  },
  {
    'src': S_NEUTRAL,
    'dst': S_ANSWER,
    'condition': lambda x: re.match("(who|what|where|when|how|why|whose|who's)", x),
    'response': "This is the answer to your question"
  },
  {
    'src': S_NEUTRAL,
    'dst': S_START,
    'condition': lambda x: embedding_cos_sim(x, "yes okay") > 0.7,
    'response': "What is it?"
  },
  {
    'src': S_NEUTRAL,
    'dst': S_END,
    'condition': lambda x: embedding_cos_sim(x, "no") > 0.7,
    'response': ""
  },
)