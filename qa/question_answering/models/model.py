import importlib
import json
import numpy as np
import os
import os.path as op
from qa.corpus_utils.preprocessing_pipeline import *
from qa.corpus_utils import ner_pipeline
from qa.corpus_utils.ner_pipeline import *
from qa.question_answering.utils import make_dataset_dict, map_words_to_named_entities
from qa.question_answering.models import *

import sys

ttv_dict = make_dataset_dict() #A dict showing which dataset (test, train, valid) each book belongs to

def map_words_to_named_entities(obj_dict, classes = ["ORG","LOC","PERSON"]):

    word2entity = {}

    for ne_class in set(classes)&set(obj_dict.keys()):
        for obj in obj_dict[ne_class]:
            for name in obj.name_variants:
                word2entity[name] = obj

    return(word2entity)


def load_np_pickle(path):
	if not path.endswith(".npy"):
		path += ".npy"
	loadobj = np.load(path, allow_pickle=True)
	return(loadobj)


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

# Use data sources in: "author", "title", "summary", "full_text_bows", "full_text_sents", "obj_list", "obj_dict", "word2entity"

active_models = {                   #module,        #class           #info source(s)  #other parameters
"cosine_distance_bow_fulltext":   ["cosine_distance_baseline", "CosineModel", 
					["full_text_sents","full_text_bows","word2idx"], {"pipeline":pipeline}],
"bert_baseline": ["bert_baseline", "BertBaseline", ["summary"], {}],
"attribute_model_fulltext": ["attribute_model", "AttributeModel", ["word2entity","obj_dict"], {}],
"character_list_model": ["character_list_model", "CharacterListModel", ["obj_dict"], {}]
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
		ft_dir = op.join(mimir_dir, "preprocessed_data", "full_texts")
	
		data_dict = {}
		title = data_dict["title"] = book_id["title"]
	
		dset = ttv_dict[title] #Test, train or valid
		
		data_dict["author"] = book_id["author"]

		data_dict["title"] = title
		data_dict["summary"] = open(op.join(mimir_dir,"data/nqa_summary_text_files", dset, title)).read()
		data_dict["full_text_bows"] = load_np_pickle(op.join(ft_dir, "bows", dset, title))
		data_dict["full_text_sents"] = open(op.join(ft_dir, "sent_tokenized", dset, title)).readlines()
		data_dict["obj_list"] = obj_list = load_np_pickle(op.join(ft_dir, "ne_obj_lists", dset, title))
		obj_types = set([obj.class_string for obj in obj_list])
		data_dict["obj_dict"] = obj_dict = {otype: [obj for obj in obj_list if obj.class_string == otype] for otype in obj_types}
		data_dict["word2entity"] = map_words_to_named_entities(obj_dict)
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
			self.select_model("bert_baseline")
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
