import importlib
import json
import os
import os.path as op
from qa.corpus_utils.preprocessing_pipeline import pipeline
from qa.question_answering.utils import make_dataset_dict
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

active_models = {                   #module,        #class           #info source   #other parameters
"bert_baseline_summary":		  ["bert_baseline", "BertBaseline", ["summary"],    {}],
"cosine_distance_bow_fulltext":   ["cosine_distance_baseline", "CosineModel", 
								   ["full_text_sents","full_text_bows","word2idx"], {"pipeline":pipeline}],
"cosine_distance_tfidf_fulltext": ["cosine_distance_baseline", "CosineModelTFIDF", 
								   ["full_text_sents","full_text_tfidf","word2idx","df_dict"], {"pipeline":pipeline}],
#"two_stage_model":				   ["two_stage_model", "TwoStageModel", "full_text", {"preloaded_model": preloaded_model}]
}

class ModelController:
	def __init__(self):
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
		return(data_dict)
			
	def confirm_book(self, book_id):
		self.current_book = book_id
		self.current_book_data = self.get_book_data_dict(book_id)

	def answer_question(self, model_id, question):
		model  = self.models_dict.get(model_id)
		data   = [self.current_book_data[ds] for ds in model.info_source]
		answer = model.answer_question(question, *data)
		return answer

if __name__ == "__main__":
	mc = ModelController()
	print(mc.models_dict)
	mc.confirm_book({"title":"2 B R 0 2 B","author":"kv"})
	while True:
		input_q = input("input question")
		print(mc.answer_question("cosine_distance_tfidf_fulltext", input_q))
