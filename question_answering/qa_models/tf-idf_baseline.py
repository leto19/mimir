import numpy as np
import os
import os.path as op
from utils import ne_BOWs_from_file, tokenize, remove_stopwords, BOWs_to_TFIDF
from collections import defaultdict
from nltk.stem.porter import PorterStemmer

mimir_dir = os.environ["MIMIR_DIR"]
stemmer = PorterStemmer()

class TFIDFModel():
	def __init__(self, valid_dir=op.join(mimir_dir,"data","nqa_summary_text_files","valid")):
		self.valid_dir=valid_dir
		self.valid_files=sorted(os.listdir(valid_dir))

	def preprocess_question(self, question):
		return([stemmer.stem(w) for w in remove_stopwords(tokenize(question))])

	def get_mean_tf_idf(self, keywords, TF_IDF_dict):
		tf_idfs = []
		for k in keywords:
			if k in TF_IDF_dict:
				tf_idfs.append(TF_IDF_dict[k])
		if len(tf_idfs) == 0:
			return 0
		else:
			return(np.mean(tf_idfs))
			

	def evaluate_question(self, question, summary_file_path):
		keywords = self.preprocess_question(question)
		BOWs = ne_BOWs_from_file(summary_file_path, stemmer=stemmer) #Bags of words per character
		TF_IDFs = BOWs_to_TFIDF(BOWs)
		character_scores = defaultdict(int)
		characters = list(BOWs.keys())
		for character in characters:
			character_scores[character] = self.get_mean_tf_idf(keywords, TF_IDFs[character])

		probabilities = {}
		character_scores_sum = sum(list(character_scores.values()))
		if character_scores_sum == 0:
			character_scores_sum = 1

		for c, s in character_scores.items():
			probabilities[c] = character_scores[c]/character_scores_sum
		print("keywords:",keywords)
		print("answers:")
		print([(c, probabilities[c]) for c in sorted(characters, key = lambda x: character_scores[x], reverse=True)][:3])
	

if __name__ == "__main__":
	mymodel = TFIDFModel()	
	while True:
		question = input("input a question\n")
		mymodel.evaluate_question(question, op.join(mimir_dir,"data","dune_plot.txt"))
