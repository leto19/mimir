import json
import re
import numpy as np
import os
import os.path as op
from collections import defaultdict
from regex_utils import all_person_regexes
from utils import spacy_get_entity_tokens, spacy_single_line, get_line_list_from_file, ntokens_spacy

mimir_dir = os.environ["MIMIR_DIR"]


def line_tokens_dict(line_list):
	prev_n_tokens = 0
	
	line_tokens_dict = {}
	for i, line in enumerate(line_list):
		n_tokens = ntokens_spacy(line)
		line_tokens_dict[i] = prev_n_tokens
		prev_n_tokens += n_tokens

	return(line_tokens_dict)


if __name__ == "__main__":

	sents_dir = op.join(mimir_dir, "preprocessed_data", "sentence_tokenized", "full_texts")
	line_tokens_dict_dir = op.join(mimir_dir, "preprocessed_data", "line_tokens_dicts","full_texts")

	dsets = ["test","train","valid"]
	
	if not op.exists(line_tokens_dict_dir):
		os.mkdir(line_tokens_dict_dir)

	for d in dsets:
		if not op.exists(op.join(line_tokens_dict_dir,d)):
			os.mkdir(op.join(line_tokens_dict_dir, d)) 


	for d in dsets:
		sents_path = op.join(sents_dir, d)
		lt_path = op.join(line_tokens_dict_dir, d)
		all_files = os.listdir(sents_path)

		for i, f in enumerate(all_files):
			base_name = f[:-6]
			if op.exists(op.join(lt_path, base_name +".npy")):
				continue
			sents_file = op.join(sents_path, f)
			sents_list = get_line_list_from_file(sents_file)
			lt_dict = line_tokens_dict(sents_list)
			np.save(op.join(lt_path,base_name), np.array([lt_dict]))
			print("{} {} of {}".format(d, i, len(all_files)))
