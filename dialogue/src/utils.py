from sentence_transformers import SentenceTransformer, util
import re

embedder = SentenceTransformer('bert-base-nli-mean-tokens')


def bold_print(text):
    '''
    Prints to console in bold text, used for system responses.
    '''
    print('\033[1m' + text + '\033[0m')

def embedding_cos_sim(user_utterance, comp_str):
  '''
  Encodes the user utterance and model answer into sentense embeddings 
  and calculates the cosine similarity between them.
  '''
  utterance_embedding = embedder.encode(user_utterance, convert_to_tensor=True)
  comp_embedding = embedder.encode(comp_str, convert_to_tensor=True)

  cos_scores = util.pytorch_cos_sim(utterance_embedding, comp_embedding)[0]
  cos_scores = cos_scores.cpu()
  return cos_scores


def is_question(user_utterance):
  '''
  Naive question detection - may need improving later as it some question
  types not covered (e.g. "Could the fellowship have flown the eagles to 
  Mordor?"). Although these may not be covered within the scope of our system.
  '''
  return (
    re.match("(who|what|where|which|when|how|why|whose|who's|is|does|has|in what|whom)", user_utterance)
  )
