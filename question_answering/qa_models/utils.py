import os
import os.path as op
import numpy as np
import csv
import nltk
from collections import defaultdict
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize 


#nqa_dir = os.environ["NARRATIVEQA_DIR"]
mimir_dir = os.environ["MIMIR_DIR"]
data_dir = op.join(mimir_dir, "data")

def tokenize(sent:str):
	return word_tokenize(sent)

def remove_stopwords(sent:list):
	stop_words = set(stopwords.words("english"))
	return ([word for word in sent if word.lower() not in stop_words and word.isalnum()])

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
	docs_csv = op.join(data_dir, "documents.csv")
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
	id_url_csv = op.join(data_dir, "id_url.csv")
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

def ne_labels_from_file(file_path):
	line_list = get_line_list_from_file(file_path)
	entity_list = []

	all_lines = " ".join([line.strip("\n") for line in line_list])
	entities = get_named_entities(tokenize(all_lines))
	return(entities)

def context_to_tokens(labelled_string: list, stemmer):
	tokens = []
	for item in labelled_string:
		if isinstance(item, nltk.tree.Tree):
			leaves = item.leaves()
			tokens += [stemmer.stem(leaf[0]) for leaf in leaves]
		else:
			tokens.append(stemmer.stem(item[0]))
	return(tokens)

def ne_BOWs_from_file(file_path, context_length=5, stemmer=None):
	ne_labels = ne_labels_from_file(file_path)
	
	BOWs_dict = defaultdict(list)

	for i, item in enumerate(ne_labels):
		if isinstance(item, nltk.tree.Tree):
			if item.label() == "PERSON":
				person_name = " ".join([leaf[0] for leaf in item.leaves()])
				before_context = ne_labels[i-context_length:i]
				after_context = ne_labels[i+1:i+1+context_length]
				BOWs_dict[person_name] += context_to_tokens(before_context + after_context, stemmer)
	
	return(BOWs_dict)

def merge_list(list_list):
	return [l for sub_l in list_list for l in sub_l]

def BOWs_to_TFIDF(BOWs_dict):
	types = list(set(merge_list(list(BOWs_dict.values()))))
	DFs = defaultdict(int)		
	for word in types:
		for BOW in BOWs_dict.values():
			if word in BOW:
				DFs[word] += 1
	
	person_TFs_dict = {}
	for person in BOWs_dict.keys():
		TFs = defaultdict(int)
		BOW = BOWs_dict[person]
		for token in BOW:
			TFs[token] += 1
		token_sum = sum(TFs.values())
		for token in TFs:
			TFs[token] = TFs[token]/token_sum
		person_TFs_dict[person] = TFs

	tf_idf_dict = defaultdict(dict)
	for person, tf_dict in person_TFs_dict.items():
		for word, tf in tf_dict.items():
			tf_idf_dict[person][word] = tf * (1/DFs[word])


#	print(tf_idf_dict)
#	import pdb; pdb.set_trace()
	return(tf_idf_dict)

def ne_list_from_file(file_path):
	line_list = get_line_list_from_file(file_path)
	entity_list = []
	
	for line in line_list: #for each sentence in the input file 
		line.strip("\n")
		t = get_tokens_from_text(line) #get tokens 
		entities = get_named_entities(t) # get entities tree
		print(entities)
		stop = input("stop? y/n")
		if stop == "y":
			import pdb; pdb.set_trace()


		for e in entities:
			if isinstance(e, nltk.tree.Tree): #it's an entity
				ent_string = " ".join([leaf[0] for leaf in e.leaves()])
				ent_tuple = (ent_string, e.label())
				import pdb; pdb.set_trace()
				
				if ent_tuple not in entity_list:
					entity_list.append(ent_tuple)
	return(entity_list)


if __name__ == "__main__":

	
	print(ne_list_from_file(op.join(mimir_dir,"data","nqa_summary_text_files","train", "Anna Karenina")))
	
	print(BOWs_to_TFIDF(ne_BOWs_from_file(op.join(mimir_dir,"data","dune_plot.txt"))))
