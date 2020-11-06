import os
import os.path as op
import argparse
import string
from qa_models.utils import csv_to_list, tokenize, make_id_name_dict
from qa_models.tfidf_baseline import TFIDFModel
from qa_models.question_classifiers import SimpleBaseline
parser = argparse.ArgumentParser


def make_qa_dict_valid(qaps_line_list):
	qa_dict_valid = {}
	for line in qaps_line_list:
		if line[0] in id_name_dict: #if it's a book
			if line[1] == "valid":
				qa_dict_valid[line[2]] = (id_name_dict[line[0]],[line[3],line[4]])
	return(qa_dict_valid)


def filter_qa_dict(qa_dict, classifier, categories):
	filtered_dict = {}
	for k in qa_dict.keys():
		question_category = classifier.classify_question(k)
		if question_category in categories:
			filtered_dict[k] = qa_dict[k]
	return(filtered_dict)


def exact_match(model, qa_dict_valid, summary_dir):
	correct_ans_file = open("correct_answers.txt","w+")
	wrong_ans_file = open("incorrect_answers.txt","w+")
	correct = 0
	n_questions = 0
	for k, value in qa_dict_valid.items():
		question = k
		summary_filepath = op.join(summary_dir, "valid", value[0])
		reference_answers = [tokenize(a) for a in value[1]]
		reference_answers = [[t for t in a if t not in string.punctuation] for a in reference_answers] 
		model_output = model.evaluate_question(question, summary_filepath)
		print("question {} of {}".format(k, len(qa_dict_valid)))
		print(question)
		print(reference_answers)
		print(model_output)	
		if tokenize(model_output) in reference_answers:
			correct += 1
			correct_ans_file.write(k + str(reference_answers) + model_output + summary_filepath +" "+"\n")
		else:
			wrong_ans_file.write(k + str(reference_answers) + model_output + summary_filepath + " " +"\n")
		n_questions +=1 
		print((correct/n_questions)*100)
	return((correct/n_questions)*100)


models_dict = {"tf_idf_baseline": TFIDFModel}

if __name__ == "__main__":

	id_name_dict = make_id_name_dict()
	nqa_dir = os.environ["NARRATIVEQA_DIR"]
	mimir_dir = os.environ["MIMIR_DIR"]
	summary_dir = op.join(mimir_dir, "data", "nqa_summary_text_files")
	full_text_dir = op.join(mimir_dir, "data", "nqa_gutenberg_corpus")
	qaps_line_list = csv_to_list(op.join(nqa_dir, "qaps.csv"))

	qa_dict_valid = make_qa_dict_valid(qaps_line_list)
	
	tf_idf_model = TFIDFModel()
	base_qc= SimpleBaseline() #baseline question classifier

	qa_dict_filtered = filter_qa_dict(qa_dict_valid, base_qc, ["PER"]) #Get only the people

	print(qa_dict_filtered)
	
	print("Exact match on full texts: {} percent".format(exact_match(tf_idf_model, qa_dict_filtered, full_text_dir)))
	#print("Exact match on summaries: {} percent".format(exact_match(tf_idf_model, qa_dict_filtered, summary_dir)))
	import pdb; pdb.set_trace()

	
