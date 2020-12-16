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

def cosine_sim_dict(vec_1, vec_2):
	"""Cosine similarity, for when vectors are stored as dictionaries"""
	vec_1 = {int(item[0]): item[1] for item in vec_1.items()} 
	vec_2 = {int(item[0]): item[1] for item in vec_2.items()} #Json is sometimes frustrating and converts dictionary keys to strings

	v1_norm = np.sqrt(sum([v**2 for v in vec_1.values()]))
	v2_norm = np.sqrt(sum([v**2 for v in vec_2.values()]))
	
	non_zeros = set(vec_1.keys()).intersection(set(vec_2.keys()))
	dot_product = sum([vec_1[k] * vec_2[k] for k in non_zeros])
	
	if v1_norm * v2_norm == 0:
		return 0

	return(dot_product/(v1_norm*v2_norm))


class CosineModel(Model):
	"""Just finds the sentence with the closest BOW embedding"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args)
		self.preprocessing_pipeline = pipeline
			# Pipeline is for the *question*, but should
			# be the same as the pipeline for the *text*

	def preprocess(self, question, word2idx):
		preprocessed_text = self.preprocessing_pipeline([question])[0]
		question_vector = sentence_to_vector(preprocessed_text, word2idx) 
		return(question_vector)
		
	def answer_question(self, question, sents, bows, word2idx):
		preprocessed_question = self.preprocess(question, word2idx)
		bows_range = list(range(len(bows)))		
		best_sent_index = max(bows_range, key= lambda x: cosine_sim_dict(bows[str(x)], preprocessed_question))
		return(self.sents[best_sent_index])

class CosineModelTFIDF(Model):
	"""Just finds the sentence with the closest BOW embedding"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args)
		self.preprocessing_pipeline = pipeline
			# Pipeline is for the *question*, but should
			# be the same as the pipeline for the *text*

	def preprocess(self, question, word2idx, df_dict, bows):
		preprocessed_text = self.preprocessing_pipeline([question])[0]
		question_vector = sentence_to_vector(preprocessed_text, word2idx)
		idf_vector = calculate_tfidf(question_vector, df_dict, len(bows))
		return(idf_vector)

	def answer_question(self, question, sents, bows, word2idx, df_dict):
		preprocessed_question = self.preprocess(question, word2idx, df_dict, bows)
		bows_range = list(range(len(bows)))		
		best_sent_index = max(bows_range, key= lambda x: cosine_sim_dict(bows[str(x)], preprocessed_question))
		#best_sent_inds = sorted(bows_range, key= lambda x: cosine_sim_dict(bows[str(x)], preprocessed_question, reversed=True))[:5]
		#import pdb; pdb.set_trace()		
		return(sents[best_sent_index])

if __name__ == "__main__":

	pass
