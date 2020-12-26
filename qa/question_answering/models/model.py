import importlib
import json
import numpy as np
import os
import os.path as op
from qa.corpus_utils.preprocessing_pipeline import *
from qa.corpus_utils.ner_pipeline import *
from qa.question_answering.utils import make_dataset_dict, map_words_to_named_entities
from qa.question_answering.models import *

import sys

dataset_dict = make_dataset_dict() #A dict showing which dataset (test, train, valid) each book belongs to

try:
	mimir_dir = os.environ["MIMIR_DIR"]
except KeyError:
	print('Please set the environment variable MIMIR_DIR')
	sys.exit(1)

class Model:
	def __init__(self, model_id:str, info_source:str):
		self.model_id = model_id
		self.info_source = info_source  #Info source is e.g. full text, summary, bag of words vectors... 
		self.book_name = None

	def answer_question(self, question, data):
		raise NotImplementedError

	def preprocess(self, question):
		raise NotImplementedError

active_models = {                   #module,        #class           #info source(s)  #other parameters
"cosine_distance_bow_fulltext":   ["cosine_distance_baseline", "CosineModel", 
								   ["full_text_sents","full_text_bows","word2idx"], {"pipeline":pipeline}],
"bert_baseline_summary":		  ["bert_baseline", "BertBaseline", ["summary"],      {}],
"cosine_distance_tfidf_fulltext": ["cosine_distance_baseline", "CosineModelTFIDF", 
								   ["full_text_sents","full_text_tfidf","word2idx","df_dict"], {"pipeline":pipeline}],
"closest_ne_summary": ["closest_ne_model", "FindNEModel",
									["summary_sents", "summary_ne_bows", "summary_ne_mentions",
									  "summary_obj_dict", "summary_line_dict"], {} ],
"closest_ne_fulltext": ["closest_ne_model", "FindNEModel",
									["full_text_sents", "full_text_ne_bows", "full_text_ne_mentions",
									  "full_text_obj_dict", "full_text_line_dict"], {} ],
"attribute_model_fulltext": ["attribute_model", "AttributeModel", ["full_text_entity2idx", "full_text_obj_dict"], {}],
"character_list_model": ["character_list_model", "CharacterListModel", ["full_text_ne_mentions","full_text_obj_dict"], {}]

#"two_stage_model":				   ["two_stage_model", "TwoStageModel", "full_text", {"preloaded_model": preloaded_model}]
}



class ModelController:
	def __init__(self, verbose=False):
		self.verbose = verbose
		self.models_dict = {}
		for model_id, model_spec in active_models.items():
			class_location, class_name, info_source, params = model_spec
			module = importlib.import_module('qa.question_answering.models.'+class_location)
			model_class = getattr(module, class_name)
			self.models_dict[model_id] = model_class(model_id, info_source, **params)
		self.current_book = None
		self.current_book_data = None
	
	def get_book_data_dict(self, book_id):
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

		data_dict["full_text_ne_mentions"] = np.load(op.join(pp_dir, "ne_mentions", "full_texts", dset, title + ".npy"), allow_pickle=True)[0]
		data_dict["full_text_obj_dict"] = np.load(op.join(pp_dir, "obj_dicts", "full_texts", dset, title + ".npy"), allow_pickle=True)[0]
		data_dict["full_text_line_dict"] = np.load(op.join(pp_dir, "line_tokens_dicts", "full_texts", dset, title + ".npy"), allow_pickle=True)[0]
		data_dict["full_text_entity2idx"] = map_words_to_named_entities(data_dict["full_text_obj_dict"])

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
			
	def confirm_book(self, book_id):
		self.current_book = book_id
		self.current_book_data = self.get_book_data_dict(book_id)

	def select_model(self, model_code):
		self.model_code = model_code
		self.model = self.models_dict.get(model_code)
		self.data = [self.current_book_data[ds] for ds in self.model.info_source]		

	def print_if_verbose(self, string):
		if self.verbose:
			print(string)

	def answer_question(self, ans_type_pred, question):		
		final_answer_type = ans_type_pred

		if ans_type_pred.endswith("ATTR"):
			self.select_model("attribute_model_fulltext")
			ans_type = ans_type_pred[:-4]
			answer = self.model.answer_question(question, *self.data, attribute=ans_type)

		elif ans_type_pred == "CHARLIST":
			self.select_model("character_list_model")
			answer = self.model.answer_question(question, *self.data, n=4)

		elif ans_type_pred == "MAINCHAR":
			self.select_model("character_list_model")
			answer = self.model.answer_question(question, *self.data, n=1)

		else:	
			self.select_model("bert_baseline_summary")
			answer = self.model.answer_question(question, *self.data)		
			final_answer_type = "bert string"

		if ans_type_pred == None:
			if answer == None:
				self.print_if_verbose("{} failed to find answer".format(self.model_code))
			else:
				self.print_if_verbose("Answer found by {}".format(self.model_code))	
		
		if ans_type_pred != None:
			if answer == None: #Backoff
				self.print_if_verbose("{} failed to find answer. Trying backoff model...".format(self.model_code))
				self.select_model("bert_baseline_summary")
				answer = self.model.answer_question(question, *self.data)
				final_answer_type = "bert string"
				if answer == None:
					self.print_if_verbose("Backoff model {} failed to find answer".format(self.model_code))
					final_answer_type = "no answer"
			if answer != None:
				self.print_if_verbose("Answer found by {}".format(self.model_code))	

		return final_answer_type, answer


if __name__ == "__main__":
	mc = ModelController()
	print(mc.models_dict)
	mc.confirm_book({"title":"2 B R 0 2 B","author":"kv"})
	while True:
		input_q = input("input question")
		print(mc.answer_question("cosine_distance_tfidf_fulltext", input_q))
