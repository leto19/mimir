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

	return bleu4_score, bleu1_score, rouge_score, cider_score
#meteor_score, 
 

def filter_qa_dict(qa_dict, classifier, categories):
	""" Get only questions with a predicted answer category"""
	filtered_dict = {}
	for k in qa_dict.keys():
		question_category = classifier.classify_question(k)
		if question_category in categories:
			filtered_dict[k] = qa_dict[k]
	return filtered_dict


def exact_match(model, qa_dict_valid, summary_dir, pause=False):
	correct_ans_file = open("correct_answers.txt", "w+")
	wrong_ans_file = open("incorrect_answers.txt", "w+")
	correct = 0
	n_questions = 0
	for k, value in qa_dict_valid.items():
		question = k
		summary_filepath = op.join(summary_dir, "valid", value[0])
		reference_answers = [tokenize(a) for a in value[1]]
		reference_answers = [[t.lower() for t in a if t not in string.punctuation] for a in reference_answers]
		model_output = model.evaluate_question(question, summary_filepath)
		os.system("clear")
		print("question {} of {}".format(n_questions + 1, len(qa_dict_valid)))
		print(question)
		print("Reference answers:", reference_answers)
		print("Model output:", model_output)
		if pause == True:
			input()
		if tokenize(model_output) in reference_answers:
			correct += 1
			correct_ans_file.write(k + str(reference_answers) + model_output + summary_filepath + " " + "\n")
		else:
			wrong_ans_file.write(k + str(reference_answers) + model_output + summary_filepath + " " + "\n")
		n_questions += 1
		print("Running total accuracy:", (correct / n_questions) * 100)
	return (correct / n_questions) * 100




class Evaluator():
	def __init__(self, valid_dict, models_dict):
		self.model_controller = ModelController()
		self.valid_dict = valid_dict
		self.models_dict = models_dict

	def evaluate_all(self):
		results = {}
		for model_id in self.models_dict:
			sorted_pairs  = sorted(list(self.valid_dict.items()))
			questions     = [item[0] for item in sorted_pairs]
			book_names    = [item[1][0] for item in sorted_pairs]
			answers_0     = [item[1][1][0] for item in sorted_pairs]
			answers_1     = [item[1][1][1] for item in sorted_pairs]

			extracted_answers = []
			for i, q in enumerate(questions):
				if book_names[i] in ["Mary: A Fiction", "Armageddon 2419 A.D."]:
					extracted_answer = ""
				else:
					print(q)
					self.model_controller.confirm_book({"title":book_names[i], "author": None})
					extracted_answer = self.model_controller.answer_question(model_id, q)
				extracted_answers.append(extracted_answer)
				print(extracted_answer)
				print("{} of {} done".format(i, len(questions))) 
			print(model_id)
			print(extracted_answers[:5])		

			bleu4_score, bleu1_score, rouge_score, cider_score = similarity_metrics(answers_0, answers_1, extracted_answers)

			results[model_id] = [bleu4_score, bleu1_score, rouge_score, cider_score]
			#print(similarity_metrics(answers_0, answers_1, extracted_answers))
		print("done")	
		import pdb; pdb.set_trace()

			#import pdb; pdb.set_trace()
			
			
			#predicted_answers = [model.evaluate
						
			#results = similarity_metrics(model, valid_dict)	


if __name__ == "__main__":

	id_name_dict = make_id_name_dict()	# Dictionary of book IDs by name
	qaps_line_list = csv_to_list(op.join(data_dir, "narrativeqa_qas.csv"))
	qa_dict_valid = make_qa_dict_valid(qaps_line_list, id_name_dict)  # Questions and answers from validation set

	full_text_dir = op.join(data_dir, "nqa_gutenberg_corpus")
	summary_dir = op.join(data_dir, "nqa_summary_text_files")


	evaluator = Evaluator(qa_dict_valid, active_models)
	evaluator.evaluate_all()
		
	exit(1)

	idx = int(input("Select the model number and press enter"))

	model, directory = models_dict[list(models_dict.keys())[idx]]

	model_instance = model()

	print("Exact match on summaries: {} percent".format(exact_match(model_instance, qa_dict_valid, directory)))
