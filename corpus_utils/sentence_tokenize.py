from utils import *
import os
import os.path as op


def file_to_sentence_tokens(file_path, gutenberg_text=False):
	with open(file_path) as text_file:
		file_lines = text_file.readlines()
	file_text = re_sub_newlines("".join(file_lines))
	
	if gutenberg_text == True:
		file_text = extract_text_from_gutenberg(file_text)
	sentence_tokens = sentence_tokenize(file_text)
	for token in sentence_tokens:
		print(token)
	import pdb; pdb.set_trace()



if __name__ == "__main__":
	file_to_sentence_tokens(op.join(data_dir, "nqa_gutenberg_corpus", "train", "2 B R 0 2 B"), gutenberg_text=True)


