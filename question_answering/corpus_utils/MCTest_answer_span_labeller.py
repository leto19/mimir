import os
import os.path as op
import re
import numpy as np
import stanfordcorenlp
nlp = stanfordcorenlp.StanfordCoreNLP("/home/jonathan/Desktop/tools/stanford-corenlp-latest/stanford-corenlp-4.1.0")
tokenize = nlp.word_tokenize

#A script for semi-automated labelling of files in the MCTest corpus. 
#Uses Levenshtein distance to automatically identify a possible answer span, which the user can then edit.
#Answers are output to a .npy file

MCTest_dir = "/home/jonathan/Desktop/corpora/MCTest"

text_file_name = "mc160.train.txt"

class bcolors:
    OKBLUE = '\033[94m'
    ENDC = '\033[0m'


mc160dev = op.join(MCTest_dir, text_file_name)

def levenshtein(input_sentence, target_sentence):

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

def normalize(text):
	return(text.lower())



with open(mc160dev) as infile:
	dev_lines = infile.readlines()


def split_by_story(file_lines):

	stories = []

	while len(file_lines) > 0:
		new_line = file_lines.pop(0)
		cond_1 = "*" * 10 in new_line
		cond_2 = len(file_lines) == 0
		if cond_1 or cond_2 :
			try:
				stories.append(story)
				story = []
			except:
				story = []
		story.append(new_line)


	return(stories)



def organize_story(story_lines):
	story_dict = {}
	assert "*" * 10 in story_lines[0]
	story_lines.pop(0)
	next_line = story_lines.pop(0)

	while " " in next_line:
		try:
			key, value = re.split(r" {2,}",next_line)
		except:
			import pdb; pdb.set_trace()
		value = value.strip("\n")
		story_dict[key] = value
		next_line = story_lines.pop(0)

	assert len(story_dict.keys()) == 3	
	
	story_text = ""

	while not next_line.startswith("1:"):
		story_text += next_line
		next_line = story_lines.pop(0)
		
	newline_to_space = str.maketrans("\n", " ")
	story_text = story_text.translate(newline_to_space).strip(" ")
	story_text = re.sub(r" {2,}", lambda x: " ", story_text) #Eliminates duplicated spaces
	story_dict["story_text"] = story_text

	qa_list = []

	while not len(qa_list) == 4:
		if re.match("[0-9]+.*", next_line):
			question = [x.strip(" \n") for x in next_line.split(":")]			
		if "*" in next_line:
			answer = next_line.split(")")[1].strip(" \n")
			qa_list.append((question, answer))
		next_line = story_lines.pop(0)


	story_dict["qa_pairs"] = qa_list
	return(story_dict)	
	

def print_indexed(token_list, color_start=None, color_end=None):
	SUP = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
	subscripts = [str(x).translate(SUP) for x in range(len(token_list))]
	zipped = [list(x) for x in list(zip(subscripts,token_list))]
	if color_start is not None:
		zipped[color_start][0] = bcolors.OKBLUE + zipped[color_start][0]
	if color_end is not None:
		zipped[color_end][1] = zipped[color_end][1] + bcolors.ENDC

	string_out = " ".join(["".join(x) for x in zipped])
	print(string_out)

def predict_answer_span(story_text, qa_pair):
	tokenized = tokenize(story_text)

	question = qa_pair[0][-1]	
	answer = qa_pair[1]


	answer = [normalize(x) for x in tokenize(answer)]

	min_distance = 1000000000
	token_start = 0
	token_end = 0

	for i in range(len(tokenized) - len(answer)): 
		sliding_window = tokenized[i:i+len(answer)]
		sliding_window = [normalize(x) for x in sliding_window]
		
		levenshtein_distance = levenshtein(sliding_window, answer)
		if levenshtein_distance < min_distance:
			min_distance = levenshtein_distance
			token_start = i
			token_end = i+len(answer)-1
		

	return(token_start, token_end)


if __name__ == "__main__":
	
	npy_name = text_file_name[:-4] + "_answer_spans.npy"

	stories = split_by_story(dev_lines)
	organized_stories = [organize_story(s) for s in stories]

	n_questions = len(organized_stories) * 4
	n = 0

	story_question_pairs = []
	
	for story in organized_stories:
		for qa_pair in story["qa_pairs"]:
			story_question_pairs.append((story["story_text"], qa_pair))

	os.system("clear")

	if not op.exists(npy_name):
		auto_answer_spans = [None] * n_questions
		corrected_answer_spans = [None] * n_questions
		answer_dict = {"auto": auto_answer_spans, "corrected": corrected_answer_spans}	
		np.save(npy_name, np.array([answer_dict]))
	else:
		answer_dict = np.load(npy_name, allow_pickle=True)[0]
		auto_answer_spans = answer_dict["auto"]
		corrected_answer_spans = answer_dict["corrected"]

	current_n = -1

	for i in range(len(corrected_answer_spans)):
		if corrected_answer_spans[i] is not None:
			current_n = i
		

	my_input = input("You have completed up to question {0}. Go to question {1}? [y/n]".format(current_n+1, current_n+2))

	if my_input == "y":
		n = current_n + 1

	while n < n_questions:

		story_text, qa_pair = story_question_pairs[n]
		tokenized = tokenize(story_text)
		token_start, token_end = predict_answer_span(story_text, qa_pair)	
		auto_answer_spans[n] = (token_start, token_end)
		
		my_input = ""
		
		while my_input not in ["y","b","na","s"]:

			print("Question {0} of {1}".format(n+1, n_questions))

			print("Q: {0}".format(qa_pair[0][-1]))
			print("A: {0}".format(qa_pair[1]))
			print_indexed(tokenized, token_start, token_end)

			print("Selected indices:\n {0} {1}".format(token_start, token_end))
			my_input = input("Correct? [y]es/[s]kip/[b]ack/[012..](new_start_index)[na](answer not in text)")
			if re.match(r"[0-9]+", my_input):
				token_start = int(my_input)

				my_input_2 = input("End correct? [y]es/[s]kip/[b]ack/[012..](new_end_index)[na](answer not in text)")
				my_input = my_input_2
			
			if re.match(r"[0-9]+", my_input):
				token_end = int(my_input)
				while token_end < token_start:
					token_end = int(input("Invalid, 2nd index must be less than or equal to 1st index. Re-enter number"))

				print_indexed(tokenized, token_start, token_end)
			os.system("clear")

		if my_input == "y":
			corrected_answer_spans[n] = (token_start, token_end)
			n += 1
			
		if my_input == "s":
			n += 1

		if my_input == "b":
			n -= 1

		if my_input == "na":
			corrected_answer_spans[n] = (-1, -1)
			n += 1
	
		np.save(npy_name, np.array([{"auto": auto_answer_spans, "corrected": corrected_answer_spans}]))	


print(string_out)
import pdb; pdb.set_trace()
