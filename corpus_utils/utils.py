import os
import os.path as op
import numpy as np
import csv
import nltk

nqa_dir = os.environ["NARRATIVEQA_DIR"]
mimir_dir = os.environ["MIMIR_DIR"]

def csv_to_list(csv_file_path):

	line_list = []
	
	with open(csv_file_path, newline="") as csvfile:
		csvreader = csv.reader(csvfile)
		for row in csvreader:
			line_list.append(row)

	return(line_list)

def list_to_csv(csv_file_path, line_list):
	
	with open(csv_file_path, "w+") as csvfile:
		csvwriter = csv.writer(csvfile)
		for row in line_list:
			csvwriter.writerow(row)


def load_or_create_object(numpy_filename: str, obj: object):
	if not numpy_filename.endswith(".npy"):
		numpy_filename += ".npy"
	if not op.exists(numpy_filename):
		return obj
	else:
		return np.load(numpy_filename, allow_pickle=True)[0]	
		

def make_id_name_dict():
	id_name_dict = {}
	docs_csv = op.join(mimir_dir, "data", "documents.csv")
	docs_list = csv_to_list(docs_csv)
	for line in docs_list[1:]:
		print(line)
		try:
			if line[2] == "gutenberg":
				id_name_dict[line[0]] = line[6]
		except:
			pass
	return(id_name_dict)

def make_name_url_dict():
	id_name_dict = make_id_name_dict()
	name_url_dict = {}
	id_url_csv = op.join(mimir_dir, "data", "id_url.csv")
	id_url_list = csv_to_list(id_url_csv)
	for line in id_url_list[1:]:
		try:
			if line[1] == "gutenberg":
				name_url_dict[id_name_dict[line[0]]] = line[2]
		except:
			pass
	return name_url_dict

def levenshtein(input_sentence, target_sentence):
	#Calculates the minimum edit distance (Levenshtein distance) between two strings (or lists)

    trellis = np.zeros((len(input_sentence) + 1, len(target_sentence) + 1))
    trellis[:,0] = np.arange(len(input_sentence)+1)
    trellis[0,:] = np.arange(len(target_sentence)+1)

    for i in range(1, len(input_sentence) + 1):
        w_in = input_sentence[i-1]
        for j in range(1, len(target_sentence) +1):
            w_t = target_sentence[j-1]
            if w_in == w_t:
                square_score = 0
            else:
                square_score = 1
            trellis[i,j] = min(trellis[i-1,j], trellis[i-1,j-1], trellis[i,j-1]) +square_score

    return(trellis[-1,-1])


def download_models():
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('maxent_ne_chunker')
    nltk.download('words')

def get_line_list_from_file(file):
    with open(file) as f:
        line_list = f.readlines()
    
    return line_list

def get_tokens_from_text(line):
    tokens = nltk.word_tokenize(line)
    
    return tokens

def get_named_entities(tokens):
    entities = nltk.chunk.ne_chunk(nltk.pos_tag(tokens))
    return entities

def ne_list_from_file(file_path):
	line_list = get_line_list_from_file(file_path)
	entity_list = list()
	for line in line_list: #for each sentence in the input file 
		line.strip("\n")
		t = get_tokens_from_text(line) #get tokens 
		entities = get_named_entities(t) # get entities tree

		for e in entities:
			if isinstance(e, nltk.tree.Tree): #it's an entity
				ent_string = " ".join([leaf[0] for leaf in e.leaves()])
				ent_tuple = (ent_string, e.label())
				if ent_tuple not in entity_list:
					entity_list.append(ent_tuple)
	return(entity_list)


if __name__ == "__main__":
	print(ne_list_from_file(op.join(mimir_dir,"data","nqa_summary_text_files","train", "Anna Karenina")))
