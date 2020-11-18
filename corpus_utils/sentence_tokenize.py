from utils import *
import os
import os.path as op


def file_to_sentence_tokens(file_path, gutenberg_text=False):
	with open(file_path) as text_file:
		file_lines = text_file.readlines()
	file_text = re_sub_newlines("".join(file_lines))
	
	
	if gutenberg_text == True:
		try:
			file_text = extract_text_from_gutenberg(file_text)
		except:
			with open("tokenization_log_file.txt", "a+") as log_file:
				log_file.write("Failed to remove end matter from {}\n".format(file_path))
	sentence_tokens = sentence_tokenize(file_text)

	return([st.strip("\n ") for st in sentence_tokens])


if __name__ == "__main__":

	in_path = op.join(data_dir, "nqa_gutenberg_corpus")	
	out_path = op.join(mimir_dir, "preprocessed_data", "sentence_tokenized", "full_texts")
	sets = ["train","test","valid"]

	with open("tokenization_log_file.txt", "w+") as log_file:  #Create a log file
		pass 
	
	for d in sets:
		set_path = op.join(out_path, d)
		if not op.exists(set_path):
			os.mkdir(set_path)


	for d in sets:
		set_path = op.join(in_path, d)
		all_files = os.listdir(set_path)
		for f in all_files:
			print("tokenizing {}".format(op.join(set_path, f)))
			sentence_tokens = file_to_sentence_tokens(op.join(set_path, f), gutenberg_text=True)
			with open(op.join(out_path, d, f + ".sents"), "w+") as out_file:
				for st in sentence_tokens:
					out_file.write(st + "\n")
		
