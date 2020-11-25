import argparse
import os
import os.path as op
import nltk
from utils import get_named_entities, tokenize,  mimir_dir, data_dir, csv_to_list, tokenize, make_id_name_dict, make_qa_dict_valid

class SimpleBaseline:
	def __init__(self):
		self.categories = {"PER", #person
						"DES", #personal description
						"LOC", #location
						"ORG", #organization
						"OTH" #other
						}

#	def preprocess_question(self, question):
#		return([stemmer.stem(w) for w in remove_stopwords(tokenize(question))])

	def classify_question(self, question):
		question_tokens = tokenize(question) 
		words_and_labels = get_named_entities(question_tokens)

		entities = [ne for ne in words_and_labels if isinstance(ne, nltk.tree.Tree)]

		labels = [e.label() for e in entities]

		who_condition = "who" in [t.lower() for t in question_tokens]
		whose_condition = "whose" in [t.lower() for t in question_tokens]
		what_condition = "what" in [t.lower() for t in question_tokens]
		where_condition = "where" in [t.lower() for t in question_tokens]
		when_condition = "when" in [t.lower() for t in question_tokens]
		why_condition = "why" in [t.lower() for t in question_tokens]
		how_condition = "how" in [t.lower() for t in question_tokens]
		
		named_person_condition = "PERSON" in labels

		if who_condition and not named_person_condition:
			return("PER") #We want a person's name
			
		if who_condition and named_person_condition:
			return("DES") #We want a person's description

		if where_condition:
			return("LOC") #Location
		
		else:
			return("OTH")

if __name__ == "__main__":

	parser = argparse.ArgumentParser()

	parser.add_argument("--int", action="store_true")
	args = parser.parse_args()

	baseline_qcl = SimpleBaseline()

	id_name_dict = make_id_name_dict()
	qaps_line_list = csv_to_list(op.join(data_dir, "narrativeqa_qas.csv"))
	qa_dict_valid = make_qa_dict_valid(qaps_line_list, id_name_dict)
	
	if args.int:
		while True:
			question = input("Input a question")
			print(baseline_qcl.classify_question(question))
	else:
		print(qa_dict_valid)
		for q, a in qa_dict_valid.items():
			os.system("clear")	
			predicted_ans_type = baseline_qcl.classify_question(q)
			print("Question:\n",q)
			print("Predicted answer type:\n", predicted_ans_type)
			print("Answers:\n",a[1][0], "/", a[1][1])	
			input("Press any key")
