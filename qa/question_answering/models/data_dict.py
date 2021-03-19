import os
import os.path as op
import numpy as np
import json

def make_book_data_dict(self, book_id):
	data_dict = {}
	title = book_id["title"]
	dset = dataset_dict[title] #Test, train or valid
	data_dict["title"] = title
	data_dict["author"] = book_id["author"]
	data_dict["summary"] = open(op.join(mimir_dir,"data/nqa_summary_text_files", dset, title)).read()
	pp_dir = op.join(mimir_dir, "preprocessed_data")
	data_dict["full_text_sents"] = open(op.join(pp_dir, "sentence_tokenized", "full_texts", dset, title + ".sents")).readlines()
	with open(op.join(pp_dir, "vocab_dicts", "full_texts", dset, title + ".vocab.json")) as json_file:
		data_dict["word2idx"] = json.load(json_file)
	with open(op.join(pp_dir, "sentence_BOWs", "full_texts", dset, title + ".bows.json")) as json_file:
		data_dict["full_text_bows"] = json.load(json_file)
	with open(op.join(pp_dir, "sentence_BOWs_TFIDF", "full_texts", dset, title + ".bows.json")) as json_file:
		data_dict["full_text_tfidf"] = json.load(json_file)
	with open(op.join(pp_dir, "document_frequency_dicts", "full_texts", dset, title + ".df_dict.json")) as json_file:
		data_dict["df_dict"] = json.load(json_file)


	with open(op.join(pp_dir, "ne_bows", "full_texts", dset, title + ".df_dict.json")) as json_file:
		data_dict["full_text_ne_bows"] = json.load(json_file)

	data_dict["full_text_ne_mentions"] = np.load(op.join(pp_dir, "ne_mentions", "full_texts", dset, title + ".npy"), allow_pickle=True)
	data_dict["full_text_obj_dict"] = np.load(op.join(pp_dir, "obj_dicts", "full_texts", dset, title + ".npy"), allow_pickle=True)[0]
	data_dict["full_text_line_dict"] = np.load(op.join(pp_dir, "line_tokens_dicts", "full_texts", dset, title + ".npy"), allow_pickle=True)[0]	
	data_dict["summary_sents"] = open(op.join(pp_dir, "sentence_tokenized", "summaries", dset, title + ".sents")).readlines()
	with open(op.join(pp_dir, "vocab_dicts", "summaries", dset, title + ".vocab.json")) as json_file:
		data_dict["summary_word2idx"] = json.load(json_file)
	with open(op.join(pp_dir, "sentence_BOWs", "summaries", dset, title + ".bows.json")) as json_file:
		data_dict["summary_bows"] = json.load(json_file)
	with open(op.join(pp_dir, "sentence_BOWs_TFIDF", "summaries", dset, title + ".bows.json")) as json_file:
		data_dict["summary_tfidf"] = json.load(json_file)
	with open(op.join(pp_dir, "document_frequency_dicts", "summaries", dset, title + ".df_dict.json")) as json_file:
		data_dict["summary_df_dict"] = json.load(json_file)
	with open(op.join(pp_dir, "ne_bows", "summaries", dset, title + ".df_dict.json")) as json_file:
		data_dict["summary_ne_bows"] = json.load(json_file)

	data_dict["summary_ne_mentions"] = np.load(op.join(pp_dir, "ne_mentions", "summaries", dset, title + ".npy"), allow_pickle=True)
	data_dict["summary_obj_dict"] = np.load(op.join(pp_dir, "obj_dicts", "summaries", dset, title + ".npy"), allow_pickle=True)[0]
	data_dict["summary_line_dict"] = np.load(op.join(pp_dir, "line_tokens_dicts", "summaries", dset, title + ".npy"), allow_pickle=True)[0]

	return(data_dict)
