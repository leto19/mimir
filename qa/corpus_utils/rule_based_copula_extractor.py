import os
import os.path as op
import numpy as np

from qa.question_answering.models.closest_ne_model import map_words_to_named_entities
from qa.question_answering.question_classifiers import replace_nes_with_type
from qa.question_answering.models.model import Model
from qa.question_answering.utils import mimir_dir
from qa.corpus_utils.ner_pipeline import *

pp_dir = op.join(mimir_dir, "preprocessed_data")

def inspect_copulas(ne_mentions, obj_dict, sents, n=4):
	"""Replaces named entities in a string with their NE type.
	We do not in fact use any NE algorithm here, just the lists of entities 
	that have been found by running NER over texts"""
	mentions_list = [mention[1][1] for mention in ne_mentions]
	#mentions_list = [l for s in mentions_list for l in s]

	characters = obj_dict["PERSON"]
	names = [(ind, max(char.name_variants, key=lambda x: len(x))) for ind, char in characters.items()]
	n_mentions = [len([ment for ment in mentions_list if ment == name[0]]) for name in names]
	results = list(zip([name[0] for name in names], n_mentions))
	results = sorted(results, key = lambda x: x[1], reverse=True)

	word2entity = map_words_to_named_entities(obj_dict, classes=["PERSON"])

	#for result in results:
	#	character = characters[result[0]]
	#	print(character)
	for sent in sents:
		try:
			sent_ne = replace_nes_with_type(sent, word2entity, obj_dict, keep_punct=True)
			if re.match(r".*PERSON, PERSON.*", sent_ne):
				print(sent)
				print(sent_ne)
				input()	
		except:
			pass

if __name__ == "__main__":

	title = "Anna Karenina"
	dset = "train"
	full_text_ne_mentions = np.load(op.join(pp_dir, "ne_mentions", "full_texts", dset, title + ".npy"), allow_pickle=True)[0]
	full_text_obj_dict = np.load(op.join(pp_dir, "obj_dicts", "full_texts", dset, title + ".npy"), allow_pickle=True)[0]
	
	full_text_sents = open(op.join(pp_dir, "sentence_tokenized", "full_texts", dset, title + ".sents")).readlines()
	inspect_copulas(full_text_ne_mentions, full_text_obj_dict, full_text_sents)
