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
	line_tokens_dict_dir = op.join(mimir_dir, "preprocessed_data", "line_tokens_dict")
	
	if not op.exists(line_tokens_dict_dir):
		os.mkdir(line_tokens_dict_dir)


	dracula_full_text = op.join(mimir_dir, "preprocessed_data/sentence_tokenized/Dracula_full_text.sents")
	base_name = "Dracula_wiki_plot"

	sents_list = get_line_list_from_file(dracula_full_text)

	print(line_tokens_dict(sents_list))
