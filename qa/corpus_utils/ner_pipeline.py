import json
import re
import numpy as np
import os
import os.path as op
from collections import defaultdict
try:
	from qa.corpus_utils.regex_utils import all_person_regexes
	from qa.corpus_utils.utils import spacy_get_entity_tokens, spacy_single_line, get_line_list_from_file, ntokens_spacy
except:
	from regex_utils import all_person_regexes
	from utils import spacy_get_entity_tokens, spacy_single_line, get_line_list_from_file, ntokens_spacy

def clash(dict1, dict2):
	""" If there is a clash between two dictionaries
		(i.e. there is at least one shared key 
			 with a different value)
			returns True
		else, returns False """

	keys1 = set(dict1.keys())
	keys2 = set(dict2.keys())
	
	both_keys = keys1.intersection(keys2)

	for k in both_keys:
		if dict1[k] != dict2[k]:
			return True
	else:
		return False

def make_ne_obj(entity_tuple):
	""" entity tuple e.g. ("Abe", "PER") """
	name, ne_class = entity_tuple
	ne_class_dict = {"PERSON": NEPerson,
					 "PER": NEPerson,
					 "LOC": NELocation,
				     "GPE": NELocation,
					 "ORG": NEOrganization,
					 "FAC": NEObj,
					"DATE": NEObj,
					 "EVENT": NEObj,
					 "WORK_OF_ART": NEObj,
					 "LAW": NEObj,
					 "LANGUAGE": NEObj,
					 "TIME": NEObj,
					 "PERCENT": NEObj,
					 "MONEY": NEObj,
					 "QUANTITY": NEObj,
					 "CARDINAL": NEObj,
					 "ORDINAL": NEObj,
					 "PRODUCT": NEObj,
					 "NORP": NEObj, #Nationality
					 }
	new_obj = ne_class_dict[ne_class](name)
	new_obj.class_string = ne_class
	#if new_obj.class_string == "PERSON":
	#	import pdb; pdb.set_trace()
	return(new_obj)

class NEObj():
	def __init__(self, name):
		self.name_variants = [name]
		self.regexes = []
		self.subnames = self.get_subnames(name)
		self.tokens = name.split(" ")
		self.combinable = False

	def __str__(self):
		return("".join(["NEObj", "\n",  
						self.class_string, "\n",
						str(self.name_variants), "\n",
						str(self.subnames), "\n"]))

	def get_subnames(self, name):
		""" returns a dictionary like:
			{"title": "Miss", "firstname": "Mina", "lastname": "Murray"}"""
		for regex in self.regexes:
			matchobj = re.match(regex, name)
			if matchobj:
				return(matchobj.groupdict())
		return({})


	def combine(self, ne_obj):
		if clash(self.subnames, ne_obj.subnames):
			raise ValueError("Subnames clash")		
		else:
			self.name_variants += ne_obj.name_variants
			self.subnames.update(ne_obj.subnames)

class NEPerson(NEObj):
	def __init__(self, name):
		super().__init__(name)
		self.regexes = all_person_regexes
		self.subnames = self.get_subnames(name)
		self.combinable = True

class NELocation(NEObj):
	def __init__(self, name):
		super().__init__(name)
		self.regexes = []
		self.subnames = self.get_subnames(name)
		self.combinable = True

class NEOrganization(NEObj):
	def __init__(self, name):
		super().__init__(name)
		self.regexes = []
		self.subnames = self.get_subnames(name)
		self.combinable = True

def first_pass(ner_function, sents_list):
	"""Returns ne_token_list e.g.[(("van Helsing", "PER"), 0.7) ...]
	"""
	ne_token_list = []

	for i, sent in enumerate(sents_list):
		entities = ner_function(sent)

		#print(entities)
		#import pdb; pdb.set_trace()
		
		ne_token_list += entities

	return(ne_token_list)

def pass_2(ner_function, sents_list, filtered_type_dict, obj_list, token_threshold):

	prev_tokens = 0

	for i, sent in enumerate(sents_list):

		entities = ner_function(sent, return_indices = True)
		for idxs, ent, token_confidence in entities:
			if ent in filtered_type_dict and token_confidence > token_threshold:
				string, class_string = ent
				for obj in obj_list:
					if not hasattr(obj, "sents"):
						obj.sents = []
					if obj.class_string == class_string and string in obj.name_variants:
						obj.sents.append(sent)

	return(obj_list)



def second_pass(ner_function, sents_list, filtered_type_dict, token_threshold):
	
	ne_bows = {}
	ne_mentions_list = []
	ne_mentions_dict = defaultdict(defaultdict)

	prev_tokens = 0

	for i, sent in enumerate(sents_list):
		sent_bow = defaultdict(int)
		entities = ner_function(sent, return_indices = True)
		for idxs, ent, token_confidence in entities:
			if ent in filtered_type_dict and token_confidence > token_threshold:
				start, end = idxs
				true_idxs = (start + prev_tokens, end + prev_tokens)
				ent_code = filtered_type_dict[ent]
				ne_mentions_list.append((true_idxs, (ent[1],ent_code)))
				if (ent[1], ent_code) in ne_mentions_dict[i].keys():
					ne_mentions_dict[i][(ent[1],ent_code)].append(true_idxs)
				else:
					ne_mentions_dict[i][(ent[1],ent_code)] = [true_idxs]
				sent_bow[ent_code] += 1

		ne_bows[i] = sent_bow
		prev_tokens += ntokens_spacy(sent)

	return(ne_bows, (ne_mentions_list, ne_mentions_dict))



def get_overall_confidence(conf_score_list):
	
	negative_probs = 1 - np.array(conf_score_list)

	return(1 - np.product(negative_probs))


def get_high_confidence_types(ne_token_list, type_confidence):
	""" Type confidence is the threshold"""

	ne_types = list(set([token for token, confidence in ne_token_list]))

	high_confidence_types = []

	for ne_type in ne_types:
		#ne_type e.g. ("van Helsing", "PER")
		confidence_list = [confidence for token, confidence in ne_token_list if token==ne_type]
		overall_confidence = get_overall_confidence(confidence_list)
		if overall_confidence > type_confidence:
			high_confidence_types.append(ne_type)

	return(high_confidence_types)


def obj_list_to_types_dict(obj_list):

	filtered_types = {}
	for i, obj in enumerate(obj_list):		

		ne_class = obj.class_string
		
		if not ne_class in filtered_types:
			filtered_types[ne_class] = defaultdict(int)		

		filtered_types[ne_class][i] = obj

	return(filtered_types)


def get_filtered_type_dict(obj_dict):
	
	filtered_type_dict = {}

	for ne_class, sub_dict in obj_dict.items():
		for idx, ne_obj in sub_dict.items():
			for name in ne_obj.name_variants:
				filtered_type_dict[(name, ne_class)] = idx
	
	return(filtered_type_dict)


def ner_pipeline(ner_function, sents_list, type_threshold = 0.999, token_threshold = 0.9):
	
	ne_token_list = first_pass(ner_function, sents_list)	

	high_confidence_types = get_high_confidence_types(ne_token_list, type_threshold)

	obj_list = combine_types_to_entities(high_confidence_types)	
 
	obj_dict = obj_list_to_types_dict(obj_list)

	filtered_type_dict = get_filtered_type_dict(obj_dict)

	ne_bows, ne_mentions_list = second_pass(ner_function, sents_list, filtered_type_dict, token_threshold)
	ne_bows = {key: {-k: v for k, v in value.items()} for key, value in ne_bows.items()}

	return(obj_dict, ne_bows, ne_mentions_list)

def combine_types_to_entities(ne_type_list):

	obj_list = [make_ne_obj(item) for item in ne_type_list]

	sorted_obj_list = sorted(obj_list, key = lambda x: len(x.subnames), reverse=True)

	#We reduce the length of the list iteratively, starting with the longest name, and combining objects if the "subnames" do not clash.
	
	#Clash example:
	# Mr. Harker, Mrs. Harker
	
	#Non-clash example:
	#J. Harker, Jonathan Harker
	i = 0

	while i < len(sorted_obj_list):
		obj_1 = sorted_obj_list[i]
		sublist = sorted_obj_list[i+1:]
		new_sublist = []
		for obj_2 in sublist:
			combinable_condition = obj_1.combinable == True and obj_2.combinable == True
			type_condition = obj_1.class_string == obj_2.class_string #They are the same NE class (e.g. PERSON)
			match_condition = len(set(obj_1.tokens)&set(obj_2.tokens)) > 0 # We check if at least one token is the same between named entities
			if combinable_condition and type_condition and match_condition and not clash(obj_1.subnames, obj_2.subnames): # And no "clash" as defined above
				obj_1.combine(obj_2) # If not, we assume named entities are the same
			else:
				new_sublist.append(obj_2)

		sorted_obj_list = sorted_obj_list[:i+1] + new_sublist
		i += 1	

	return(sorted_obj_list)	

if __name__ == "__main__":
	
	mimir_dir = os.environ["MIMIR_DIR"]

	#dracula_full_text = op.join(mimir_dir, "data/dracula_wiki_plot.txt")
	#dracula_full_text = op.join(mimir_dir, "preprocessed_data/sentence_tokenized/Dracula_full_text.sents")


	obj_dict_dir = op.join(mimir_dir, "preprocessed_data", "obj_dicts")
	ne_bows_dir = op.join(mimir_dir, "preprocessed_data", "ne_bows")
	ne_mentions_list_dir = op.join(mimir_dir, "preprocessed_data", "ne_mentions")

	for folder in [ne_mentions_list_dir, ne_bows_dir, obj_dict_dir]:
		if not op.exists(folder):
			os.mkdir(folder)

	#base_name = "Dracula_wiki_plot"	

	in_dir = op.join(mimir_dir, "preprocessed_data/sentence_tokenized/full_texts")
	obj_dict_dir = op.join(mimir_dir, "preprocessed_data", "obj_dicts","full_texts")
	ne_bows_dir = op.join(mimir_dir, "preprocessed_data", "ne_bows","full_texts")
	ne_mentions_list_dir = op.join(mimir_dir, "preprocessed_data", "ne_mentions","full_texts")

	dsets = ["test", "train", "valid"]
	
	for folder in [ne_mentions_list_dir, ne_bows_dir, obj_dict_dir]:
		if not op.exists(folder):
			os.mkdir(folder)
		for dset in dsets:
			if not op.exists(op.join(folder, dset)):
				os.mkdir(op.join(folder, dset))

	for dset in dsets:
		for i, filename in enumerate([fn for fn in os.listdir(op.join(in_dir, dset)) if fn.endswith("sents")]):
			print("doing {} set {} of {}".format(dset, i, len(os.listdir(op.join(in_dir, dset)))))
			base_name = filename[:-6]
			#if op.exists(op.join(ne_bows_dir, dset, base_name + ".df_dict.json")):
			#	continue
			sents_list = get_line_list_from_file(op.join(in_dir, dset, filename))
			obj_dict, ne_bows, ne_mentions_list = ner_pipeline(spacy_single_line, sents_list)
			print(obj_dict, ne_bows, ne_mentions_list)
			import pdb; pdb.set_trace()
			with open(op.join(ne_bows_dir, dset, base_name + ".df_dict.json"), "w") as dump_path:
				json.dump(ne_bows, dump_path)
			np.save(op.join(ne_mentions_list_dir, dset, base_name), np.array(ne_mentions_list))
			np.save(op.join(obj_dict_dir, dset, base_name), np.array([obj_dict]))
