import numpy as np
import os
import os.path as op
from corpus_utils.preprocessing_pipeline import pipeline
from utils import ne_BOWs_from_file, tokenize, remove_stopwords, BOWs_to_TFIDF
from collections import defaultdict
from nltk.stem.porter import PorterStemmer

mimir_dir = os.environ["MIMIR_DIR"]
stemmer = PorterStemmer()

class CosineModel():
	"""Just finds the sentence with the closest BOW embedding"""
	def __init__(self, valid_dir=op.join(mimir_dir,"data","nqa_summary_text_files","valid")):
		self.valid_dir=valid_dir
		self.valid_files=sorted(os.listdir(valid_dir))

	def preprocess_question(self, question):
		return([stemmer.stem(w) for w in remove_stopwords(tokenize(question))])	

	def evaluate_question(self, question, filepath):
		preprocessed
		return(max(characters, key=lambda x: character_scores[x]))

if __name__ == "__main__":
	mymodel = TFIDFModel()	
	while True:
		question = input("input a question\n")
		mymodel.evaluate_question(question, op.join(mimir_dir,"data","dune_plot.txt"))
