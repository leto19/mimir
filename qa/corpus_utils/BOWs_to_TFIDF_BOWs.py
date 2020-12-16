import json
import numpy as np
import os 
import os.path as op

mimir_dir = os.environ["MIMIR_DIR"]

def convert_to_int(json_dict):
	""" Saving as Json converts ints to stings, so we convert back"""
	out_dict = {}
	for k in json_dict.keys():
		sub_dict = json_dict[k]
		sub_dict_out = {}
		for j in sub_dict.keys():
			sub_dict_out[int(j)] = sub_dict[j]
		out_dict[int(k)] = sub_dict_out
	return(out_dict)

def make_document_frequency_dict(bows_dict):
	all_words_idxs = set([sl for l in [sub_dict.keys() for sub_dict in list(bows_dict.values())] for sl in l])
	df_dict = {idx: len([bow for bow in bows_dict.values() if idx in bow]) for idx in all_words_idxs}
	return(df_dict)

def calculate_tfidf(bow, df_dict, N):
	"""N is N 'documents', or in this case, sentences"""
	df_dict = {int(k):int(v) for k, v in df_dict.items()}
	idf_bow = {k: v*np.log(N/df_dict[k]) for k,v in bow.items() if k != -1}
	return(idf_bow)

def make_tfidf_dict(bow_vecs_dict, df_dict):
	tf_idf_dict = {}
	for key, bow in bow_vecs_dict.items():
		tf_idf_dict[key] = calculate_tfidf(bow, df_dict, len(bow_vecs_dict))
	return(tf_idf_dict)


if __name__ == "__main__":

	in_path = op.join(mimir_dir, "preprocessed_data", "sentence_BOWs", "full_texts")
	out_path = op.join(mimir_dir, "preprocessed_data", "sentence_BOWs_TFIDF", "full_texts")
	dict_path = op.join(mimir_dir, "preprocessed_data", "vocab_dicts", "full_texts")
	df_dict_path = op.join(mimir_dir, "preprocessed_data", "document_frequency_dicts", "full_texts")
	sets = ["valid","train","test"]

	with open("preprocessing_log_file.txt", "w+") as log_file:	#Create a log file
		pass 
	
	for d in sets:
		set_path = op.join(out_path, d)
		if not op.exists(set_path):
			os.mkdir(set_path)

	for d in sets:
		set_path = op.join(in_path, d)
		all_files = os.listdir(set_path)
		dict_set_path = op.join(dict_path, d)
		for f in all_files:
			base_name = f.split(".")[0]
			with open(op.join(set_path,base_name + ".bows.json")) as json_file:
				bow_vectors = json.load(json_file)
			with open(op.join(dict_set_path, base_name + ".vocab.json")) as json_file:
				word2idx = json.load(json_file)
			print("Making BOW from {}".format(op.join(set_path, f)))
			bow_vecs_dict = convert_to_int(bow_vectors)
			df_dict = make_document_frequency_dict(bow_vecs_dict)
			
			tf_idf_dict = make_tfidf_dict(bow_vecs_dict, df_dict)
			with open(op.join(out_path, d, base_name + ".bows.json"), "w") as dump_path:			
				json.dump(tf_idf_dict, dump_path)
			
			with open(op.join(df_dict_path, d, base_name + ".df_dict.json"), "w") as dump_path:			
				json.dump(df_dict, dump_path)
