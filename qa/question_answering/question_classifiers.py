import argparse
import re
import os
import os.path as op
import nltk
try:
	from qa.question_answering.utils import get_named_entities, tokenize,  mimir_dir, data_dir, csv_to_list, tokenize, make_id_name_dict, make_qa_dict_valid, levenshtein
	from qa.question_answering.models.closest_ne_model import map_words_to_named_entities
except:

	from utils import get_named_entities, tokenize,  mimir_dir, data_dir, csv_to_list, tokenize, make_id_name_dict, make_qa_dict_valid, levenshtein
#	from models.closest_ne_model import map_words_to_named_entities

def in_lowercased(question, word):
	question_tokens = tokenize(question)
	if " ".join(word) in " ".join([t.lower() for t in question_tokens]):
		return True
	return False

def in_named_entities(question, pattern):
	raise NotImplementedError

def replace_nes_with_type(string, word2entity, obj_dict):
	"""Replaces named entities in a string with their NE type.
	We do not in fact use any NE algorithm here, just the lists of entities 
	that have been found by running NER over texts"""

	removepunct = str.maketrans("","","?!.,-")
	
	string = string.lower().translate(removepunct)

	nes_longest_first = sorted(word2entity.keys(), key = lambda x: len(x), reverse=True)

	for ne in nes_longest_first:
		if ne.lower() in string:
			for ne_class, sub_dict in obj_dict.items():
				if word2entity[ne] in sub_dict:
					string = re.sub(ne.lower(), ne_class, string)

	return string
	
def sentence_match(sentence, question_patterns):
	""" If the sentence is "close enough" (in terms of Levenshtein distance)
	to one of any given patterns, will return True. Otherwise, false """
	t_sentence = tokenize(sentence)

	for pattern in question_patterns:
		if t_sentence == tokenize(pattern): #There may be a more flexible way to check this. 
			return True

	return False

def make_sm_lambda(pattern):
	return lambda x: sentence_match(x, pattern)

def make_lambda(function, pattern):
	return lambda x: function(x, pattern)

attribute_sents = ["what is PERSON's {}","what is the {} of PERSON"]

attributes_canonical = ["titleATTR","firstnameATTR", "surnameATTR","middlenamesATTR"]
attributes_classes = [["title"],["first name", "firstname"],["surname","last name", "family name"],["middle name"]]


attribute_question_patterns = [[x for sublist in [[s.format(c) for c in ac] for s in attribute_sents] for x in sublist] for ac in attributes_classes] 
# ^Don't question it.
#print(attribute_question_patterns)
#exit(1)


attribute_patterns_classes = [(make_sm_lambda(attribute_question_patterns[i]),attributes_canonical[i]) 
										for i in range(len(attributes_canonical))]

class QuestionClassifier():
	def __init__(self):
		self.patterns_list = [
		*attribute_patterns_classes,
		(make_lambda(in_lowercased, ["list","of","characters"]), "CHARLIST"),
		(make_lambda(in_lowercased, ["main","characters"]), "CHARLIST"),
		(make_lambda(in_lowercased, ["character", "list"]), "CHARLIST"),
		(make_lambda(in_lowercased, ["most","important","characters"]), "CHARLIST"),
		(make_lambda(in_lowercased, ["main", "character"]), "MAINCHAR"),
		(make_lambda(in_lowercased, ["protagonist"]), "MAINCHAR")
		#(lambda x: in_lowercased("who", x) and not in_named_entities("PER", x), "PER"),
				#We want a person's name
		#(lambda x: in_lowercased("who", x) and in_named_entities("PER", x), "DESC"),
				 #We want a personal description
			]

		
	def predict(self, question):
		"""Iterates through the categories in self.patterns list in order;
			once one is matched, returns that category."""
		for match_function, category in self.patterns_list:
			preprocessed_question = replace_nes_with_type(question, self.word2entity, self.obj_dict)
			if match_function(preprocessed_question):
				return category
		
		return("Nope")

	def set_data_dict(self, data_dict):
		self.data_dict = data_dict
		self.obj_dict = data_dict["full_text_obj_dict"]
		self.word2entity = map_words_to_named_entities(self.obj_dict)

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
		
		if [t.lower() for t in question_tokens[:2]] == ["how", "many"]:
			return("NUM") #Number


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
