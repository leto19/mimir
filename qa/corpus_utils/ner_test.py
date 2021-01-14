from bisect import bisect_left
import nltk
import numpy as np
import os 
import os.path as op
import re
import matplotlib.pyplot as plt
from termcolor import cprint
from utils import load_or_create, tokenize, stop_words
gazeteer_file = op.join(os.environ["CORPORA"],"allCountries.txt")
dracula_file = op.join(os.environ["MIMIR_DIR"], "preprocessed_data","sentence_tokenized", "Dracula_full_text.sents")

def get_places_list(gazeteer_file):

	places_list = []
	with open(gazeteer_file) as gfile:
		while True:
			line = gfile.readline()
			if not line:
				break
			line = line.split("	")
			places_list.append(line[1])
	return(sorted(places_list))



likely_patterns = {"LOC": ["far from LOC"],
					"PER": ["said PER", "PER said", "PER gave", "PER wrote", "when PER had gone", "PER came with me", "PER was sleeping", "PER returned"]}



def get_line_frequency(named_entity, lines):
	named_entity_re = ("\W").join(named_entity.split(" "))
	frequency = []
	for line in lines:
		frequency.append(len(re.findall(named_entity_re, line)))
	return(frequency)

if __name__ == "__main__":
	
	#places_list = load_or_create("places_list", lambda: get_places_list(gazeteer_file), save=False)
	with open(dracula_file) as dfile:
		dracula_lines = dfile.readlines()
	#places_set = set(places_list)	
	
	from regex_utils import name_regex, NameObject

	all_names = []

	for line in dracula_lines:
		print(line)
		match_objects = re.finditer(name_regex, line)
		print("new line")
		discovered_names = [m for m in list(match_objects)] 
		for name in discovered_names:
			nobj = NameObject(name)
			print(nobj)
			input()
		print(discovered_names)
		#if "de Jon" in "+++".join(discovered_names) and not "Helsing" in "+++".join(discovered_names):
		#	input()
		all_names += discovered_names
	
	strip_re = "[^A-Za-z]*(?P<name>.*?)[^A-Za-z]*$"

	all_names = [re.sub(strip_re, lambda x: x.group("name"), name) for name in all_names] #Remove trailing punctuation and spaces
	names_set = list(set(all_names))

	names_set_tups = [(name, len([n for n in all_names if n == name])) for name in names_set]

	print(sorted(names_set_tups, key = lambda x: x[1])) 
	
	np.save("discovered_names", np.array(all_names))
	#print(all_names)

	n_bins = len(dracula_lines) // 10
	for word in names_set:
		for i, w2 in enumerate(names_set):
			if len(set(word.split(" ")).intersection(set(w2.split(" ")))) != 0 and word != w2:
				w1_freqs = get_line_frequency(word, dracula_lines)
				w2_freqs = get_line_frequency(w2, dracula_lines)
				n_splits = len(w1_freqs)//10
				for i in range(len(w1_freqs)):
					if w1_freqs[i] > 0: 
						w1_freqs[i] -= w2_freqs[i]
				
				w1_split = np.split(np.array(w1_freqs[:-(len(w1_freqs)%10)]), n_splits)
				w2_split = np.split(np.array(w2_freqs[:-(len(w2_freqs)%10)]), n_splits)
				w1_bins = np.sum(w1_split, axis=1)
				w2_bins = np.sum(w2_split, axis=1)
				w3_freqs = get_line_frequency(names_set[(i+1) % len(names_set)], dracula_lines)
				w3_split = np.split(np.array(w3_freqs[:-(len(w3_freqs)%10)]), n_splits)
				w3_bins = np.sum(w3_split, axis=1)
				#min_length = min([len(w1_hist), len(w2_hist), len(w3_hist)])
				correlation = np.corrcoef(w1_bins, w2_bins)[0,1]
				print(word, "|", w2, "|", correlation)
				print(word, "|", names_set[(i +1) % len(names_set)], "|", np.corrcoef(w1_bins, w3_bins)[0,1])
				input()
				
	import pdb; pdb.set_trace()


	for line in dracula_lines:
		tokens = tokenize(line) + ["."]
		tags = [t[1] for t in nltk.pos_tag(tokens[:-1])]
		ne_start_ind = None
		for i, token in enumerate(tokens): 
			if re.match("[A-Z]", token[0]) and token not in stop_words and tags[i] == "NNP":
				if not ne_start_ind:
					ne_start_ind = i
			else:
				if ne_start_ind:
					ne_end_ind = i - 1
					potential_ne = " ".join(tokens[ne_start_ind:ne_end_ind + 1])
					print(potential_ne)
					if potential_ne in places_set:	
						tokens[ne_start_ind] = '\033[94m' + tokens[ne_start_ind]
						tokens[ne_end_ind] = tokens[ne_end_ind] + '\033[0m' # print tokens in blue
					ne_start_ind = None
		labelled = " ".join(tokens[:-1])
		print(labelled)
		input()
	
	import pdb; pdb.set_trace()

