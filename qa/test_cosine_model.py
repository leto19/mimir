import os
import os.path as op
from corpus_utils.preprocessing_pipeline import pipeline, sentence_to_vector
from corpus_utils.BOWs_to_TFIDF_BOWs import calculate_tfidf
from question_answering.models.cosine_distance_baseline import CosineModel, cosine_sim_dict

mimir_dir = os.environ["MIMIR_DIR"]

def sentence_pipeline(sentence: str, word2idx, df_dict=None, N=None):
	""" Takes a sentence and a word: index dictionary, and performs preprocessing
		followed by converting to a BOW vector"""
	return(sentence_to_vector(pipeline([sentence])[0], word2idx))

def sentence_pipeline_tfidf(sentence: str, word2idx, df_dict, N):
	"""Same as above, but converts vector to tf-idf vector"""
	bow = sentence_pipeline(sentence, word2idx)
	tf_idf_bow = calculate_tfidf(bow, df_dict, N)
	return(tf_idf_bow)	

if __name__ == "__main__":

	sents_fp = op.join(mimir_dir, "preprocessed_data/sentence_tokenized/full_texts/valid/The Deerslayer.sents")
	#print(sents_fp)
	mymodel = CosineModel(sentence_pipeline_tfidf)
	#mymodel.evaluate_question("what is a deer?", sents_fp)
	sent1 = "I like the sea"
	sent2 = "I am the sea"
	sent3 = "I like deer"

	sents =  [sent1, sent2, sent3]
	
	"sentence_BOWs_TFIDF"
	
#vectorized_sents = [sentence_pipeline(sent, mymodel.word2idx) for sent in [sent1, sent2, sent3]]

	#for i, sent in enumerate(vectorized_sents):
	#	for j, sent_ in enumerate(vectorized_sents):
	#		print(sents[i], sents[j], cosine_sim_dict(sent, sent_))

	while True:
		question = input("input a question\n")
		print(mymodel.evaluate_question(question, sents_fp))
