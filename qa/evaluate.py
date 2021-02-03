import numpy as np
import string # to get a list of punctuation
import sys
import os
import os.path as op
import argparse
import importlib
import string
from collections import OrderedDict
from qa.question_answering.utils import mimir_dir, data_dir, csv_to_list, tokenize, make_id_name_dict, \
	make_qa_dict_valid
from qa.question_answering.models.bert_baseline import BertBaseline
from qa.question_answering.models.model import ModelController, active_models
from qa.question_answering.question_classifiers import SimpleBaseline
from pycocoevalcap.meteor.meteor import Meteor
from pycocoevalcap.cider.cider import Cider
from pycocoevalcap.rouge.rouge import Rouge
from pycocoevalcap.bleu.bleu import Bleu

parser = argparse.ArgumentParser

def similarity_metrics(ref1_strs, ref2_strs, extracted_answers):
	
	for argument in [ref1_strs, ref2_strs, extracted_answers]:
		if type(argument[0]) != str:
			raise TypeError("""
		All arguments passed to similarity_metrics must be	
		lists of untokenized sentences, e.g. 
			["The cat sat on the mat", 
			 "The man ate the hotdog", ...]""")

	meteor_obj = Meteor()
	rouge_obj = Rouge()
	cider_obj = Cider()
	bleu_obj = Bleu(4)

	word_target_dict = {}
	word_response_dict = {}

	for i in range(len(ref1_strs)):
		word_target_dict[i] = [ref1_strs[i], ref2_strs[i]]
		word_response_dict[i] = [extracted_answers[i]]

	bleu_score, bleu_scores = bleu_obj.compute_score(
		word_target_dict, word_response_dict)
	bleu1_score, _, _, bleu4_score = bleu_score
	bleu1_scores, _, _, bleu4_scores = bleu_scores
	#meteor_score, meteor_scores = meteor_obj.compute_score(
	#	word_target_dict, word_response_dict)
	rouge_score, rouge_scores = rouge_obj.compute_score(
		word_target_dict, word_response_dict)
	cider_score, cider_scores = cider_obj.compute_score(
		word_target_dict, word_response_dict)
	accuracy_score = exact_match(ref1_strs, ref2_strs, extracted_answers)

	return bleu4_score, bleu1_score, rouge_score, cider_score, accuracy_score 

def filter_qa_dict(qa_dict, classifier, categories):
	""" Get only questions with a predicted answer category"""
	filtered_dict = {}
	for k in qa_dict.keys():
		question_category = classifier.classify_question(k)
		if question_category in categories:
			filtered_dict[k] = qa_dict[k]
	return filtered_dict


def tokenize_and_lowercase(strings):
	strings = [tokenize(s) for s in strings]
	strings = [[t.lower() for t in s if t not in string.punctuation] for s in strings] 
	return(strings)

def exact_match(ref1_strs, ref2_strs, extracted_answers):
	n_questions = len(extracted_answers)
	ref1_strs = tokenize_and_lowercase(ref1_strs)	
	ref2_strs = tokenize_and_lowercase(ref2_strs)	
	extracted_answers = tokenize_and_lowercase(extracted_answers)	
	correct = 0
	for i in range(len(extracted_answers)):
		if extracted_answers[i] == ref1_strs[i] or extracted_answers[i] == ref2_strs[i]:
			correct += 1
	return (correct / n_questions) * 100


class Evaluator():
	def __init__(self, valid_dict, models_dict):
		self.model_controller = ModelController()
		self.valid_dict = valid_dict
		self.models_dict = models_dict
		sorted_pairs  = sorted(list(self.valid_dict.items()))
		self.questions	   = [item[0] for item in sorted_pairs]
		self.book_names    = [item[1][0] for item in sorted_pairs]
		self.answers_1	   = [item[1][1][1] for item in sorted_pairs]
		self.answers_0	   = [item[1][1][0] for item in sorted_pairs]

	def answer_all_questions(self, model_id):
		mc = self.model_controller
		extracted_answers = []
		questions = self.questions
		last_book = None	

		for i, q in enumerate(questions):
			print("evaluating q {} of {}".format(i+1, len(questions)))
			os.system('clear')
			book = self.book_names[i]
			if book != last_book:
				mc.confirm_book({"title":book, "author": None})
				mc.select_model(model_id) #This is to load in the book data
			extracted_answer = mc.model.answer_question(q, *mc.data)
			extracted_answers.append(extracted_answer)
			last_book = book
		return(extracted_answers)

	def score(self, extracted_answers):
		bleu4_score, bleu1_score, rouge_score, cider_score, accuracy_score = similarity_metrics(self.answers_0, self.answers_1, extracted_answers)
		return(bleu4_score, bleu1_score, rouge_score, cider_score, accuracy_score) 

	def evaluate_model(self, model_id):
		extracted_answers = self.answer_all_questions(model_id)
		scores = self.score(self, extracted_answers)
		return(scores)		

	def evaluate_all(self):
		results = {}
		for model_id in self.models_dict:

			bleu4_score, bleu1_score, rouge_score, cider_score, accuracy_score = similarity_metrics(self.answers_0, self.answers_1, extracted_answers)
			results[model_id] = [bleu4_score, bleu1_score, rouge_score, cider_score, accuracy_score]
		
		return results


if __name__ == "__main__":

	id_name_dict = make_id_name_dict()	# Dictionary of book IDs by name
	qaps_line_list = csv_to_list(op.join(data_dir, "narrativeqa_qas.csv"))
	qa_dict_valid = make_qa_dict_valid(qaps_line_list, id_name_dict)  # Questions and answers from validation set

	evaluator = Evaluator(qa_dict_valid, active_models)
	evaluator.evaluate_all()
		
	exit(1)

	idx = int(input("Select the model number and press enter"))

	model, directory = models_dict[list(models_dict.keys())[idx]]

	model_instance = model()

	print("Exact match on summaries: {} percent".format(exact_match(model_instance, qa_dict_valid, directory)))

#summary_dir = op.join(data_dir, "nqa_summary_text_files")
#full_text_dir = op.join(data_dir, "nqa_gutenberg_corpus")
