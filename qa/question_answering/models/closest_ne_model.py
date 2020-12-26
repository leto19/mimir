import json
import sys
import numpy as np
import os
import os.path as op
from collections import defaultdict
from nltk.stem.porter import PorterStemmer
from qa.corpus_utils.preprocessing_pipeline import pipeline, sentence_to_vector
from qa.corpus_utils.BOWs_to_TFIDF_BOWs import calculate_tfidf
from qa.question_answering.models.model import Model
from qa.question_answering.models.cosine_distance_baseline import cosine_sim_dict

try:
	mimir_dir = os.environ["MIMIR_DIR"]
except KeyError:
	print('Please set the environment variable MIMIR_DIR')
	sys.exit(1)
stemmer = PorterStemmer()


def map_words_to_named_entities(obj_dict, classes = ["ORG","LOC","PERSON"]):

	word2entity = {}

	for ne_class in set(classes)&set(obj_dict.keys()):
		for idx, obj in obj_dict[ne_class].items():
			for name in obj.name_variants:
				word2entity[name] = idx

	return(word2entity)

class FindNEModel(Model):
	"""Finds closest named embedding"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args)
		self.preprocessing_pipeline = pipeline
			# Pipeline is for the *question*, but should
			# be the same as the pipeline for the *text*

	def preprocess(self, question, word2entity):
		question = question.lower()
		word2entity = {k.lower():v for k, v in word2entity.items()}
		question_vector = {}
		for k, v in word2entity.items():
			if k.lower() in question:
				question_vector[v] = 1	
		return(question_vector)
		
	def answer_question(self, question, sents, ne_bows, ne_mentions, obj_dict, linedict, ne_type="PERSON"):
		for key, bow in ne_bows.items():
			ne_bows[key] = {abs(int(k)): abs(int(v)) for k, v in bow.items()}
		ne_mentions_list, ne_mentions_dict = ne_mentions
		word2entity = map_words_to_named_entities(obj_dict)
		print(word2entity)
		preprocessed_question = self.preprocess(question, word2entity)
		print(preprocessed_question)
		ne_bows_range = list(range(len(ne_bows)))		
		best_sent_index = max(ne_bows_range, key= lambda x: cosine_sim_dict(ne_bows[str(x)], preprocessed_question))
		top_bow = ne_bows[str(best_sent_index)]
		print(ne_bows)
		print("top bow",top_bow)
		top_sent_mentions = ne_mentions_dict[best_sent_index]
		shared_nes = set([int(k) for k in top_bow.keys()])&set(preprocessed_question.keys())
		print(shared_nes)
		search_index = np.mean([top_sent_mentions[k] for k in top_sent_mentions if k[1] in [k for k in shared_nes]])
		best_search_index = min(ne_mentions_list, key = lambda x: abs(np.mean(x[0]) - search_index))
		found_ne_object = obj_dict[best_search_index[1][0]][best_search_index[1][1]]
		return(str(found_ne_object))

if __name__ == "__main__":

	pass
