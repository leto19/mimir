import json
from qa.corpus_utils.utils import mimir_dir, remove_stopwords
from collections import defaultdict
import os
import os.path as op
import numpy as np
from nltk.tokenize import word_tokenize
from nltk.stem.porter import PorterStemmer

stemmer = PorterStemmer()

def load_sentences_to_list(file_path):
	with open(file_path) as lines_file:
		lines = lines_file.readlines()
	return lines

def json_dump(obj, file_path):
	with open(file_path, 'w') as fp:
		json.dump(obj, fp)


def sentence_to_vector(sentence:list, word2idx):
	""" Makes a sparse BOW vector, stored as a dictionary to save space (i.e. with no zeros)
		e.g. if "are" is token 3 and "dogs" is token 500, the sentence "Dogs are dogs"
		would be stored as:
		 {3: 1, 500: 2}
						"""
	ids = [word2idx.get(word,-1) for word in sentence]
	vector = defaultdict(int)
	for idx in ids:
		vector[idx] += 1
	return(vector)

def make_dictionaries(sents_list):
	"""Makes a dictionary of the sort idx: word,
		and the reverse. 
			e.g. {"the": 0, "horse": 0 ...}"""
	sents_flattened = [s for l in sents_list for s in l] #Makes list of sentences into list of words
	words_set = set(sents_flattened)
	word2idx = {word:i for i, word in enumerate(words_set)}
	idx2word = {i:word for i, word in enumerate(words_set)}
	return(word2idx, idx2word)

def file_pipeline(file_path):
	sentences = load_sentences_to_list(file_path)
	return(sents_to_vecs(sentences))

def sents_to_vecs(sentences):
	"""Name may infringe copyright :P"""
	stemmed_sents = pipeline(sentences)
	word2idx, idx2word = make_dictionaries(stemmed_sents)
	BOW_vectors = {i: sentence_to_vector(sent, word2idx) for i, sent in enumerate(stemmed_sents)}
	return(BOW_vectors, idx2word)

def pipeline(sentences):
	"""This is our full preprocessing pipeline """
	if type(sentences) != list:
		raise TypeError
	tokenized_sents = [word_tokenize(s) for s in sentences]
	no_stopwords = [remove_stopwords(s) for s in sentences]
	stemmed_sents = [[stemmer.stem(w) for w in s] for s in tokenized_sents]
	return(stemmed_sents)


	
if __name__ == "__main__":
	

	in_path = op.join(mimir_dir, 

	exit(1)
	#Below is the loop over NQA

	in_path = op.join(mimir_dir, "preprocessed_data", "sentence_tokenized", "full_texts")
	out_path = op.join(mimir_dir, "preprocessed_data", "sentence_BOWs", "full_texts")
	dict_path = op.join(mimir_dir, "preprocessed_data", "vocab_dicts", "full_texts")
	sets = ["valid","train","test"]

	with open("preprocessing_log_file.txt", "w+") as log_file:	#Create a log file
		pass 
	
	for d in sets:
		set_path = op.join(out_path, d)
		if not op.exists(set_path):
			os.mkdir(set_path)
		set_path_dict = op.join(dict_path, d)
		if not op.exists(set_path_dict):
			os.mkdir(set_path_dict)

	for d in sets:
		set_path = op.join(in_path, d)
		all_files = os.listdir(set_path)
		for f in all_files:
			print("Making BOW from {}".format(op.join(set_path, f)))
			bow_vectors, idx2word = file_pipeline(op.join(set_path, f))
			base_name = f.split(".")[0]
			json_dump(bow_vectors, op.join(out_path, d, base_name + ".bows.json"))
			json_dump(idx2word, op.join(dict_path, d, base_name + ".vocab.json"))
