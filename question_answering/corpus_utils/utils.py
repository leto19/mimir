import os
import os.path as op
import numpy as np
import csv

nqa_dir = os.environ["NARRATIVEQA_DIR"]

	

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
	docs_csv = op.join(nqa_dir, "documents.csv")
	docs_list = csv_to_list(docs_csv)
	for line in docs_list[1:]:
		print(line)
		try:
			if line[2] == "gutenberg":
				id_name_dict[line[0]] = line[6]
		except:
			pass
	return(id_name_dict)

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
