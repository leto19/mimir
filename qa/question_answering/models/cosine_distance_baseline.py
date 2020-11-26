import json
import numpy as np
import os
import os.path as op
from collections import defaultdict
from nltk.stem.porter import PorterStemmer

mimir_dir = os.environ["MIMIR_DIR"]
stemmer = PorterStemmer()

def cosine_sim_dict(vec_1, vec_2):
	"""Cosine similarity, for when vectors are stored as dictionaries"""
	v1_norm = sum([np.sqrt(int(v)) for v in vec_1.values()])**2
	v2_norm = sum([np.sqrt(int(v)) for v in vec_2.values()])**2
	
	non_zeros = set(vec_1.keys()).intersection(set(vec_2.keys()))
	dot_product = sum([vec_1[int(k)] * vec_2[int(k)] for k in non_zeros])
	
	if v1_norm * v2_norm == 0:
		return 0

	return(dot_product/(v1_norm*v2_norm))


class CosineModel():
	"""Just finds the sentence with the closest BOW embedding"""
	def __init__(self, preprocessing_pipeline):
		self.preprocessing_pipeline = preprocessing_pipeline
			# Pipeline is for the *question*, but should
			# be the same as the pipeline for the *text*
		self.sents_file_path = None
		self.bows_file_path = None
		self.text_bows = None #A dictionary containing BOW vectors (as dictionaries)

	def preprocess(self, question):
		return(pipeline([question], self.word2idx)[0][0])

	def set_file_path(self, sents_file_path):
		self.sents_file_path = sents_file_path
		file_path_split = sents_file_path.split("/")
		root = op.join(*file_path_split[:-4])
		dset = file_path_split[-2]
		base_name = file_path_split[-1].split(".")[0]
		self.bows_file_path = op.join("/",root, "sentence_BOWs", "full_texts", dset, base_name + ".bows.json")
		self.word2idx_file_path = op.join("/", root, "vocab_dicts", "full_texts", dset, base_name + ".vocab.json")


	def set_bows_file(self, text_bows):
		self.text_bows = text_bows
		

	def evaluate_question(self, question, sents_file_path):
		if sents_file_path != self.sents_file_path:
			self.set_file_path(sents_file_path)
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
		print(preprocessed_question)	

		best_sent_index = max(text_bows_range, key= lambda x: cosine_sim_dict(self.text_bows[str(x)], preprocessed_question))
		
		best_sent_idxs = sorted(text_bows_range, key= lambda x: cosine_sim_dict(self.text_bows[str(x)], preprocessed_question), reverse=True)
		print(best_sent_idxs)
		print(np.array(self.sents)[best_sent_idxs][:10])	
		return(self.sents[best_sent_index])


if __name__ == "__main__":

	sents_fp = op.join(mimir_dir, "preprocessed_data/sentence_tokenized/full_texts/valid/The Deerslayer.sents")
	print(sents_fp)
	mymodel = CosineModel()	
	while True:
		question = input("input a question\n")
		print(mymodel.evaluate_question(question, sents_fp))
