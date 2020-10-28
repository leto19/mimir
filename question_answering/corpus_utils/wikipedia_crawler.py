import re
import os
import os.path as op
import wikipedia
from sparknotes_book_list import get_nqa_books_list
from utils import list_to_csv

mimir_dir = os.environ["MIMIR_DIR"]
data_dir = op.join(mimir_dir, "data")

def camelCase_to_space(regexp_match):
	rm = regexp_match[0]
	return (rm[0] + "\n" + rm[1:3])

double_quotes_to_single = str.maketrans('"',"'")

name_description_regex = re.compile("((?:\(?'?[A-Z]\S*[a-z]+'?\)?[\s]?)+?)(?:\s?([\,\:\–\—]\s?|(is|\-)\s))(.{4,})")
		#Any # of Capitalized Words, followed by [,-:] or "is", followed by a string of at least length 4

def preprocess_wiki_string(wiki_string):
	wiki_string_a = re.sub(r"[a-z][A-Z][a-z]", camelCase_to_space, wiki_string)
		#Some examples of "camel case" appear when the wikipedia API fails to separate
		#section titles and character names, e.g. House AtreidesPaul Atreides.
	wiki_string_b = wiki_string_a.translate(double_quotes_to_single)
		#changing " to ' as otherwise would play havoc with .csv format
	return(wiki_string_b)

def get_characters_section(page_text):
	characters_section = re.search(r"[^=]==[^=\n]*haracter[^=\n]*==[^=](.*?)[^=]==[^=]", page_text, re.DOTALL)
							#Finds all text after under a 2nd level heading containing the string "haracter"
	if characters_section:
		return(characters_section[1])
	else:
		characters_section = re.search(r"[^=]===[^=\n]*haracter[^=zn]*===[^=](.*?)[^=]===[^=]", page_text, re.DOTALL)
							#Finds all text after under a 3rd level heading containing the string "haracter"
	if characters_section:
		return(characters_section[1])
	else:
		return None

def get_character_list(novel_name):
	print(novel_name)
	try:
		wikipage = wikipedia.page(novel_name)
	except:
		print("Wikipedia page {} not found".format(novel_name))
		return([])
	content_string = wikipage.content
	characters_string = get_characters_section(content_string)
	if characters_string is None:
		print("No characters section")
		return([])
	characters_string = preprocess_wiki_string(characters_string)
	lines = characters_string.split("\n")
	
	csv_lines = []

	for line in lines:
		matchobj = re.match(name_description_regex, line)
		if matchobj:
			csv_lines.append([novel_name, matchobj[1], matchobj[4]])
			print(matchobj[1])
			print(matchobj[4])
		else:
			print("no match")
			print(line)

	return(csv_lines)


if __name__ == "__main__":

	books_list = get_nqa_books_list()

	all_lines = []

	for novel in books_list:
		all_lines += get_character_list(novel)
	
	list_to_csv(op.join(data_dir,"wikipedia_character_descriptions"),all_lines)
