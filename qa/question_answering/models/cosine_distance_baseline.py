import json
import numpy as np
import os
import os.path as op
from collections import defaultdict
from nltk.stem.porter import PorterStemmer
from qa.question_answering.models.model import Model

mimir_dir = os.environ["MIMIR_DIR"]
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
	def __init__(self, model_id, preprocessing_pipeline, tf_idf=True):
		Model.__init__(self, model_id)
		self.preprocessing_pipeline = preprocessing_pipeline
			# Pipeline is for the *question*, but should
			# be the same as the pipeline for the *text*
		self.tf_idf = tf_idf
		self.sents_file_path = None
		self.bows_file_path = None
		self.text_bows = None #A dictionary containing BOW vectors (as dictionaries)

	def preprocess(self, question):
		if self.tf_idf:
			return(self.preprocessing_pipeline(question, self.word2idx, self.df_dict, len(self.text_bows)))
		else:
			return(self.preprocessing_pipeline(question, self.word2idx))

	def set_file_path(self, sents_file_path):
		self.sents_file_path = sents_file_path
		file_path_split = sents_file_path.split("/")
		root = op.join(*file_path_split[:-4])
		dset = file_path_split[-2]
		base_name = file_path_split[-1].split(".")[0]
		if self.tf_idf:
			self.bows_file_path = op.join("/",root, "sentence_BOWs_TFIDF", "full_texts", dset, base_name + ".bows.json")
			self.df_dict_file_path = op.join("/",root, "document_frequency_dicts", "full_texts", dset, base_name + ".df_dict.json")
		else:
			self.bows_file_path = op.join("/",root, "sentence_BOWs", "full_texts", dset, base_name + ".bows.json")
		self.word2idx_file_path = op.join("/", root, "vocab_dicts", "full_texts", dset, base_name + ".vocab.json")


	def set_bows_file(self, text_bows):
		self.text_bows = text_bows
		

	def evaluate_question(self, question, sents_file_path):
		if sents_file_path != self.sents_file_path:
			self.set_file_path(sents_file_path)
			if self.tf_idf:
				with open(self.df_dict_file_path) as f_obj:
					read_obj = f_obj.read()
					df_dict = json.loads(read_obj)
					self.df_dict = {int(k): v for k, v in df_dict.items()}
			with open(self.bows_file_path) as f_obj:
				read_obj = f_obj.read()
				self.text_bows = json.loads(read_obj)
			with open(self.word2idx_file_path) as f_obj:
				read_obj = f_obj.read()
				self.word2idx = json.loads(read_obj)
			with open(self.sents_file_path) as f_obj:
				self.sents = f_obj.readlines()
		preprocessed_question = self.preprocess(question)
		text_bows_range = list(range(len(self.text_bows)))		
		best_sent_index = max(text_bows_range, key= lambda x: cosine_sim_dict(self.text_bows[str(x)], preprocessed_question))

		best_sent_idxs = sorted(text_bows_range, key= lambda x: cosine_sim_dict(self.text_bows[str(x)], preprocessed_question), reverse=True)
		best_sents = np.array(self.sents)[best_sent_idxs[:5]]
		for i, sent in enumerate(best_sents):
			print(i+1,". ", sent) 
		return(self.sents[best_sent_index])


if __name__ == "__main__":

	pass
