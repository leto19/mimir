import re
import os
import os.path as op
import numpy as np
import csv
import nltk
import spacy
from nltk.corpus import stopwords 
from collections import defaultdict

nlp = spacy.load("en_core_web_sm")

mimir_dir = os.environ["MIMIR_DIR"]

data_dir = op.join(mimir_dir, "data")


stop_words = set(stopwords.words("english"))

def remove_newline(text):
	newline_trans = str.maketrans("", "", "\n") 
	return(text.translate(newline_trans))

def re_sub_newlines(text):
	return (re.sub(r"(?<=\S)\n(?=\S)", lambda x: " ", text))		

def newline_to_space(text):
	newline_trans = str.maketrans("\n", " ") 
	return(text.translate(newline_trans))

#def sentence_tokenize(text): 
#	return (re.split(r'(?<=(?<!\WMr|\WDr|Mrs|\WMs|\WSr|\WJr|.\WM|\WSt|.\..|.\s[A-Z])[\.\?\!])\s+', text)) #Just split text on "." "?" or "!" 
							#Avoids those abbreviations ^



#def return

def handle_abbreviations(matchobj):	
	print(matchobj)
	newlinerepl = str.maketrans("\n", " ")
	if matchobj.group("abbrvs"): #If there are any abbreviations, or we are at the 
									#end of a line, we do not split
		print("no split")
		#input()
		out = matchobj[0]
		if matchobj.group("trailing"):
			out = out[:-len(matchobj.group("trailing"))]
			out += matchobj.group("trailing").translate(newlinerepl)
#			print(matchobj)
#			print(matchobj.groups())
#			if "\n" in matchobj[0]:
#				print(matchobj.groups())
#				print(matchobj.group("trailing"))
#				this = input()
#				if this == "1":
#					import pdb; pdb.set_trace()
	
		return (out)
	else:
		print("split")
		#input()
		return matchobj[0] + "😠" # Our extremely arbitrary "split" token



def handle_newline(matchobj):	
	print(matchobj)
	if matchobj[1]: #If there are any abbreviations, or we are at the 
									#end of a line, we do not split
		return (matchobj[0])
	else:
		print("split")
		#input()
		return matchobj[0] + "😠" # Our extremely arbitrary "split" token


def sentence_tokenize(text):

	alt_punct = str.maketrans(".?!", "。？！")
	revert_punct = str.maketrans("。？！", ".?!")

	new_text = re.sub(r'".*?"', lambda x: x[0].translate(alt_punct), text) #Changes .?! inside quotation marks to
																		#alternate chars 。？！ so we will not split
																		#on them

#[\W\s\_]&&[^\n]

	abbreviations = "(?P<abbrvs>(Mr|Mrs|Ms|Dr|Sr|Jr|M|St|Cl|No)|[\.A-Z]+)"
	split_punct = "[\.?!]"
	split_re = re.compile(r"" + abbreviations + "?" + "(?P<trailing>" + split_punct + "[\s\n]*)")
	new_text = re.sub(split_re, handle_abbreviations, new_text)
	
	new_line = re.compile(r"[\s\n]*\n[\s]*(😠)?") # if we are at a new line, we will split anyway
	new_text = re.sub(new_line, handle_newline, new_text)
	new_text = new_text.translate(revert_punct)	

	print(new_text)

	return(new_text.split("😠"))

	
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


def load_or_create(numpy_filename: str, create_function, save=False):
	"""Loads a numpy object if the path exists, or, if it doesn't, creates
		it with create_function. If save == True, also saves the object"""

	if not numpy_filename.endswith(".npy"):
		numpy_filename += ".npy"
	
	if not op.exists(numpy_filename):
		output = create_function()
	else:
		return np.load(numpy_filename, allow_pickle=True)[0]	
	
	if save == True:
		if isinstance(output, np.ndarray):
			np.save(numpy_filename, output)
		elif isinstance(output, list):
			np.save(numpy_filename, np.array(output))
		else:
			np.save(numpy_filename, np.array([output]))
	
	return(output)

def extract_text_from_gutenberg(text):
	text = re.split(r"\*\*\*.*?START.*?PROJECT GUTENBERG EBOOK.*?\*\*\*", text)[1]
	text = re.split(r"\*\*\*.*?END.*?PROJECT GUTENBERG EBOOK.*?\*\*\*", text)[0]
	return(text)

def make_id_name_dict():
	id_name_dict = {}
	docs_csv = op.join(mimir_dir, "data", "documents.csv")
	docs_list = csv_to_list(docs_csv)
	for line in docs_list[1:]:
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


def remove_stopwords(sent:list):
	stop_words = set(stopwords.words("english"))
	return ([word for word in sent if word.lower() not in stop_words])


def tokenize(line):
	tokens = nltk.word_tokenize(line)	 
	return tokens


def spacy_single_line(line, return_indices = False):
	doc = nlp.make_doc(line)
	beams = nlp.entity.beam_parse([doc], beam_width=16, beam_density=0.0001)
	entity_scores = defaultdict(float)
	parses = nlp.entity.moves.get_beam_parses(beams[0])
	for score, ents in parses:
	#	print (score, ents)
		for start, end, label in ents:
			# print ("here")
			entity_scores[(start, end, label)] += score
	#print ('entity_scores', entity_scores)
	best_parse = parses[0][1]
	ents = nlp(line).ents
	tokens = []
	for ent in ents:
		score = entity_scores[(ent.start, ent.end, ent.label_)]
		if return_indices == False:
			tokens.append(((ent.text, ent.label_),score))
		else:
			tokens.append(((ent.start, ent.end),(ent.text, ent.label_),score))
	return(tokens)
	
def ntokens_spacy(line):
	doc = nlp(line)
	return(len(doc))

def spacy_get_entity_types(line_list):
	all_ents = []
	for line in line_list:
		processed = nlp(line)
		for ent in processed.ents:
			new_entity = [ent.text,ent.label_]
			if new_entity not in all_ents:
				all_ents.append(new_entity)
	return(all_ents)


def spacy_get_entity_tokens(line_list):
	all_ents = []
	for line in line_list:
		all_ents += spacy_single_line(line)
	return(all_ents)


def get_named_entities(tokens):
	entities = nltk.chunk.ne_chunk(nltk.pos_tag(tokens))
	return entities

def ne_list_from_file(file_path):
	line_list = get_line_list_from_file(file_path)
	entity_list = list()
	for line in line_list: #for each sentence in the input file 
		line.strip("\n")
		t = tokenize(line) #get tokens 
		entities = get_named_entities(t) # get entities tree

		for e in entities:
			if isinstance(e, nltk.tree.Tree): #it's an entity
				ent_string = " ".join([leaf[0] for leaf in e.leaves()])
				ent_tuple = (ent_string, e.label())
				if ent_tuple not in entity_list:
					entity_list.append(ent_tuple)
	return(entity_list)


if __name__ == "__main__":
	sents = "\n".join(get_line_list_from_file(op.join(mimir_dir,"preprocessed_data","sentence_tokenized","summaries","train", "Anna Karenina.sents")))

	spacy_single_line(sents)
#	spacy_single_line("This is a line with the name Harry in it. He went to Anatole France.")
	#print(ne_list_from_file(op.join(mimir_dir,"data","nqa_summary_text_files","train", "Anna Karenina")))
