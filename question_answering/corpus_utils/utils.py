import numpy as np
import csv

def csv_to_list(csv_file_path):

	line_list = []
	
	with open(csv_file_path, newline="") as csvfile:
		csvreader = csv.reader(csvfile)
		for row in csvreader:
			line_list.append(row)

	return(line_list)

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
