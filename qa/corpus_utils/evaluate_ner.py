import nltk
import numpy as np
import os 
import os.path as op
import re
from multiset import Multiset
from utils import load_or_create, tokenize, stop_words, ne_list_from_file, spacy_get_entities

#all the characters in sparknotes
gold_standard_people = [["Dracula","Count Dracula","the Count"],["Abraham Van Helsing", "Van Helsing", "Dr. Van Helsing", "Professor Van Helsing"], ["Mina","Miss Murray", "Mina Murray", "Miss Mina Murray", "Madam Mina", "Mina Harker", "Mrs. Harker"], ["Lucy", "Lucy Westenra", "Miss Westenra"], ["Jonathan Harker", "Jonathan","Harker", "Mr. Harker"], ["Arthur Holmwood", "Lord Godalming", "Arthur", "Holmwood", "Mr. Holmwood", "Hon. Arthur Holmwood"], ["John Seward","Dr. Seward", "Dr. John Seward", "John"], ["Quincey Morris", "Mr. Quincey P. Morris", "Quincey", "Mr. Morris", "Morris"], ["Renfield", "Mr. Renfield", "R. M. Renfield"], ["Mrs. Westenra"]]

gold_standard_places = [["England"], ["Transylvania"], ["the Carpathian Mountains", "the Carpathians"], ["Bukovina"], ["Moldavia"], ["Exeter"], ["Castle Dracula", "the Castle"], ["Varna"], ["Whitby"], ["Buda-Pesth", "Budapest"], ["London"]]

def entity_recall(ner_list, gold_standard):
	""" Recall for finding *at least one* name per entity"""
	flattened_ner = list(np.concatenate(ner_list))
	true_pos = 0
	for entity in gold_standard:
		if len(set(flattened_ner).intersection(set(entity))) > 0:
			true_pos += 1
	return true_pos/ len(gold_standard_people)

def names_recall(ner_list, gold_standard):	
	flattened_ner = list(np.concatenate(ner_list))
	flattened_gs = list(np.concatenate(gold_standard))
	true_pos = 0
	for entity in flattened_gs:
		if entity in flattened_ner:
			true_pos += 1
	return true_pos/ len(flattened_gs)

def names_precision(ner_list, entity_type):
	n_correct = 0	
	for i, name in enumerate(ner_list):
		print("evaluate name {} of {}".format(i+1, len(ner_list)))
		print(name)
		if entity_type[0] in "aeiouAEIOU":
			y_or_n = input("Is this an {} [y/n]".format(entity_type))
		else:
			y_or_n = input("Is this a {} [y/n]".format(entity_type))
		if y_or_n == "y":
			n_correct += 1
		os.system("clear")
	return (n_correct / len(ner_list))

def get_subset_pairs(subset_list):
	subset_pairs = []
	for subset in subset_list:
		name_pairs = [(i, j) for i in subset for j in subset if i != j]
		subset_pairs.append(name_pairs)
	return([s for l in subset_pairs for s in l])

def rand_index(ner_list, gold_standard):
	""" Modified version of Rand index, only deals with recall"""
	gold_standard_pairs = Multiset(get_subset_pairs(gold_standard))
	ner_list_pairs = Multiset(get_subset_pairs(ner_list))
	return(len(gold_standard_pairs.intersection(ner_list_pairs))/len(gold_standard_pairs))

def evaluate_precision_and_recall(ner_list, gold_standard, entity_type, skip_precision = "skip precision"):
	""" Gold standard should be a list of lists in which co-referent entities belong to the same sub-list""" 
	
	results_dict = {}
	flattened_gs = list(np.concatenate(gold_standard))	
	flattened_ner = list(np.concatenate(ner_list))

	results_dict["entity_recall"] = entity_recall(ner_list, gold_standard)
	results_dict["names_recall"] = names_recall(ner_list, gold_standard)

	filtered_ner_list = [list(filter(lambda x: x in flattened_gs, sublist)) for sublist in ner_list]	
	filtered_ner_list = list(filter(lambda x: len(x) > 0, filtered_ner_list))
	filtered_gold_standard = [list(filter(lambda x: x in flattened_ner, sublist)) for sublist in gold_standard]	
	filtered_gold_standard = list(filter(lambda x: len(x) > 0, filtered_gold_standard))

	results_dict["rand_index"] = rand_index(filtered_ner_list, filtered_gold_standard)
	flattened_ner = list(np.concatenate(ner_list))
	if not skip_precision:
		results_dict["names_precision"] = names_precision(flattened_ner, entity_type)
	return(results_dict)

def print_results(results_dict, method_code):
	print("***", method_code, "***")
	print("Recall based on entities discovered:")
	print(results_dict["entity_recall"])
	print("Recall based on names discovered:")	
	print(results_dict["names_recall"])
	print("Rand index (measure of accuracy of clustering**): \n **of the names which were correct")
	print(results_dict["rand_index"])
	if "names_precision" in results_dict:
		print("Names precision:")
		print(results_dict["names_precision"])
	
	
if __name__ == "__main__":
	data_dir = op.join(os.environ["MIMIR_DIR"], "data")	

	skip_precision = True if input("Skip precision? (requires hand-labelling) [y/n]") == "y" else False

	dracula_wiki_plot = op.join(data_dir, "dracula_wiki_plot.txt")
	dracula_full_text = op.join(data_dir, "Dracula_full_text.txt")
	nltk_person_list = [[ent[0]] for ent in ne_list_from_file(dracula_wiki_plot) if ent[1] == "PERSON"]
	spacy_entities = spacy_get_entities(dracula_wiki_plot)
	spacy_person_list = [[ent[0]] for ent in spacy_entities if ent[1] == "PERSON"]
	
	nltk_results = evaluate_precision_and_recall(nltk_person_list, gold_standard_people, "person", skip_precision=skip_precision)
	spacy_results = evaluate_precision_and_recall(spacy_person_list, gold_standard_people, "person", skip_precision=skip_precision)

	print_results(nltk_results, "NLTK for people")
	print_results(spacy_results, "Spacy for people")
