import json
import sys
import numpy as np
import os
import os.path as op
from collections import defaultdict
from nltk.stem.porter import PorterStemmer
from qa.question_answering.models.model import Model
from qa.corpus_utils.preprocessing_pipeline import pipeline, sentence_to_vector
from qa.corpus_utils.BOWs_to_TFIDF_BOWs import calculate_tfidf

try:
	mimir_dir = os.environ["MIMIR_DIR"]
except KeyError:
	print('Please set the environment variable MIMIR_DIR')
	sys.exit(1)
stemmer = PorterStemmer()


class FindNEModel(Model):
	"""Finds closest named embedding"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args)
		self.preprocessing_pipeline = pipeline
			# Pipeline is for the *question*, but should
			# be the same as the pipeline for the *text*

	def preprocess(self, question, word2idx):
		question_vector = sentence_to_vector(preprocessed_text, word2entity) 
		return(question_vector)
		
	def answer_question(self, question, sents, ne_bows, ne_mentions, obj_dict, linedict, ne_type="PERSON"):
		ne_mentions_list, ne_mentions_dict = ne_mentions
		word2entity = map_words_to_named_entities(obj_dict)
		preprocessed_question = self.preprocess(question, word2entity)
		ne_bows_range = list(range(len(bows)))		
		best_sent_index = max(bows_range, key= lambda x: cosine_sim_dict(bows[str(x)], preprocessed_question))
		top_bow = ne_bows[best_sent_index]
		top_sent_mentions = ne_mentions_dict[best_sent_index]
		shared_nes = set(top_bow.keys())&set(preprocessed_question.keys())
		search_index = np.mean([top_sent_mentions[k] for k in top_sent_mentions.keys() if k[0] in [k for k in shared_nes.keys()])
		best_search_index = min(bows_range, key = lambda x: abs(mean(ne_mentions_list[x][0]) - search_index))
		found_ne_object = ne_mentions_list[best_search_index][0]
		return(found_ne_object)

if __name__ == "__main__":

	pass
