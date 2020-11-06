import os
import os.path as op
import argparse
from qa_models.utils import csv_to_list, tokenize, make_id_name_dict
from qa_models.tfidf_baseline import TFIDFModel
parser = argparse.ArgumentParser

id_name_dict = make_id_name_dict()
#nqa_dir = os.environ["NARRATIVEQA_DIR"]
mimir_dir = os.environ["MIMIR_DIR"]
summary_dir = op.join(mimir_dir, "data", "nqa_summary_text_files")
qaps_line_list = csv_to_list(op.join(mimir_dir, "data", "nqa_qas.csv"))

def make_qa_dict_valid(qaps_line_list):
	qa_dict_valid = {}
	for line in qaps_line_list:
		if line[0] in id_name_dict: #if it's a book
			if line[1] == "valid":
				qa_dict_valid[line[2]] = (id_name_dict[line[0]],[line[3],line[4]])
	return(qa_dict_valid)

qa_dict_valid = make_qa_dict_valid(qaps_line_list)

models_dict = {"tf_idf_baseline": TFIDFModel}

def exact_match(model, qa_dict_valid):
	correct_ans_file = open("correct_answers.txt","w+")
	wrong_ans_file = open("incorrect_answers.txt","w+")
	correct = 0
	n_questions = 0
	for k, value in qa_dict_valid.items():
		question = k
		summary_filepath = op.join(summary_dir, "valid", value[0])
		reference_answers = [tokenize(a) for a in value[1]]
		model_output = model.evaluate_question(question, summary_filepath)
		
		
		if tokenize(model_output) in reference_answers:
			correct += 1
			correct_ans_file.write(k + str(reference_answers) + model_output + summary_filepath +" "+"\n")
		else:
			wrong_ans_file.write(k + str(reference_answers) + model_output + summary_filepath + " " +"\n")
		n_questions +=1 
		print((correct/n_questions)*100)
	return((correct/n_questions)*100)

if __name__ == "__main__":
	
	tf_idf_model = TFIDFModel()

	print("Exact match: {} percent".format(exact_match(tf_idf_model, qa_dict_valid)))
	
