from bisect import bisect_left
import nltk
import numpy as np
import os 
import os.path as op
import re
from termcolor import cprint
from list_of_honorifics import honorifics_dict
from utils import load_or_create, tokenize, stop_words
gazeteer_file = op.join(os.environ["CORPORA"],"allCountries.txt")
dracula_file = op.join(os.environ["MIMIR_DIR"], "preprocessed_data","sentence_tokenized", "Dracula_full_text.sents")

#all the characters in sparknotes
gold_standard_people = [["Dracula","Count Dracula","the Count"],["Abraham Van Helsing", "Van Helsing", "Dr. Van Helsing", "Professor Van Helsing"], ["Mina","Miss Murray", "Mina Murray", "Miss Mina Murray", "Madam Mina", "Mina Harker", "Mrs. Harker"], ["Lucy", "Lucy Westenra", "Miss Westenra"], ["Jonathan Harker", "Jonathan","Harker", "Mr. Harker"], ["Arthur Holmwood", "Lord Godalming", "Arthur", "Holmwood", "Mr. Holmwood", "Hon. Arthur Holmwood"], ["John Seward","Dr. Seward", "Dr. John Seward", "John"], ["Quincey Morris", "Mr. Quincey P. Morris", "Quincey", "Mr. Morris", "Morris"], ["Renfield", "Mr. Renfield", "R. M. Renfield"], ["Mrs. Westenra"]]

gold_standard_places = [["England"], ["Transylvania"], ["the Carpathian Mountains", "the Carpathians"], ["Bukovina"], ["Moldavia"], ["Exeter"], ["Castle Dracula", "the Castle"], ["Varna"], ["Whitby"], ["Buda-Pesth", "Budapest"], ["London"]]



def n_reps(regex):
	return("(" + regex + ")*")

def a_or_b(regex1, regex2):
	return("(" + regex1 + ")|(" + regex2 + ")")

def option_list(regex_list):
	return("(" + "|".join(regex_list) + ")")

def opt(regex):
	""" Make a regex optional"""
	return("(" + regex + ")?")

def named(regex, name):
	return("(?P<" + name + ">" + regex + ")")

def named_opt(regex, name):
	return("(?P<" + name + ">" + regex + ")?")

#honorifics_dict = {"common_titles": common_titles, "formal_titles": formal_titles, "professional_religious_titles", professional_religious_titles, "post_nominals": post_nominals, "following_his_her": following_his_her}

cap_word = "[A-Z][a-z]+"
middlenames = "[A-Za-z\s]+"

of_multilingual = option_list(["Mc","Mac", "O'","de ", "di ", "von ", "van ", "bin ", "d'", "du ","des ", "del ", "della ", "de la ", "de los", "de las ", "van der ", "dos ", "zu ", "auf "]) 

surname = a_or_b(cap_word, of_multilingual + cap_word)
initial = "[A-Z]\."
initials = "[A-Z\.\s]+"
all_titles = honorifics_dict["common_titles"] + honorifics_dict["formal_titles"] + honorifics_dict["professional_religious_titles"]
post_nominals = honorifics_dict["post_nominals"]

title        = option_list([title for title in all_titles]) + "\.?" 
post_nominal = option_list([pn for pn in post_nominals])

first_name_regex = "".join([named_opt(title, "title0"),
							named(cap_word, "firstname0"),              
							opt(named(n_reps(initial),"initials0")), 
							named_opt(cap_word, "surname0")])         #First name is the only non-optional element

surname_regex    = "".join([named_opt(title, "title1"), 
							named_opt(cap_word, "firstname1"), 
							opt(named(n_reps(initial),"initials1")), 
							named(cap_word, "surname1")])                #Surname is the only non-optional element

middlename_regex = "".join([named_opt(title, "title2"), 
							named(cap_word, "firstname2"), 
							named(n_reps(cap_word),"middlenames0"), 
							named(cap_word, "surname2")])  

the_title_regex = "[Tt]he " + named(title, "title3") #For things like "the Count"



title_singleword =                "\s".join([named(title,"title"), cap_word]) + "$"
title_initials_surname = 		  "\s".join([named(title, "title"),  
								  named(initials, "firstinitials"), 
								  named(surname, "surname")]) + "$"
title_firstname_initials_surname = "\s".join([named(title, "title"), 
								  named(cap_word, "firstname"),
								  named(initials, "middleinitials"), 
								  named(surname, "surname")]) + "$"
title_firstname_middlenames_surname = "\s".join([named(title,"title"),
								  named(cap_word, "firstname"),
								  named(middlenames, "middlenames"),
								  named(surname, "surname")]) + "$"
title_firstname_surname = "\s".join([named(title,"title"),
								  named(cap_word, "firstname"),
								  named(surname, "surname")]) + "$"
singleword = cap_word + "$"
initials_surname = "\s".join([named(initials, "firstinitials"),
						      named(surname, "surname")]) + "$"
firstname_initials_surname = "\s".join([named(cap_word, "firstname"),
										named(initials, "middleinitials"),
										named(surname, "surname")]) + "$"
firstname_middlename_surname =  "\s".join([named(cap_word, "firstname"),
								  named(middlenames, "middlenames"),
								  named(surname, "surname")]) + "$"
firstname_surname = "\s".join([named(cap_word, "firstname"),
								  named(surname, "surname")]) + "$"
initials                     = named(initials, "fullinitials") + "$"
the_title                    = "\s".join(["the", named(title, "title")]) + "$"


all_person_regexes = [title_singleword, title_initials_surname, title_firstname_initials_surname, title_firstname_middlenames_surname, title_firstname_surname, singleword, initials_surname, firstname_initials_surname, firstname_middlename_surname, firstname_surname, initials, the_title]

name_regex = "(?!<[A-Za-z])" + option_list([middlename_regex, first_name_regex, surname_regex, the_title_regex])


class NameObject():
	def __init__(self, matchobj, line_no=None):
		self.span = matchobj.span
		self.line_no = line_no
		self.mentions = [(self.line_no, self.span)]
		self.dict_keys = ["title", "firstname", "initials", "middlenames"]
		self.full_name = self.strip_punctuation(matchobj[0])
		matchobj_dict = matchobj.groupdict()
		self.title = self.strip_non_full_stop(matchobj_dict["title0"] or matchobj_dict["title1"] or matchobj_dict["title2"] or matchobj_dict["title3"])
		self.first_name = self.strip_punctuation(matchobj_dict["firstname0"] or matchobj_dict["firstname1"] or matchobj_dict["firstname2"])
		self.middle_names = self.strip_punctuation(matchobj_dict["middlenames0"])
		self.initials = self.strip_non_full_stop(matchobj_dict["initials0"] or matchobj_dict["initials1"])
		self.surname = self.strip_punctuation(matchobj_dict["surname0"] or matchobj_dict["surname1"] or matchobj_dict["surname2"])
		self.set_base_name()
		if self.first_name == self.base_name:  #If we only have one name, we can't be too sure if it's a first name or surname
			self.first_name = None
		if self.surname == self.base_name:     #See above comment
			self.surname = None
		self.variants = [self.full_name]

	def __str__(self):
		return("".join(["Full name: ", str(self.full_name), "\n",
						"Base name: ", str(self.base_name), "\n",
						"Title: ",     str(self.title), "\n",
						"First name: ", str(self.first_name), "\n",
						"Middle names: ", str(self.middle_names), "\n",
						"Initials: ", str(self.initials), "\n",
						"Surname: ", str(self.surname), "\n"]))
									
	def set_base_name(self):
		self.base_name = ""
		if self.first_name:
			self.base_name += self.first_name + " "
		if self.middle_names:
			self.base_name += self.middle_names + " "
		if self.initials:
			if not self.middle_names: 
				self.base_name += self.initials + " "
		if self.surname:
			self.base_name += self.surname
		self.base_name = self.strip_non_full_stop(self.base_name) if self.base_name else ""
		if self.title:
			self.full_name = self.title + " " + self.base_name
		else: 
			self.full_name = self.base_name
		self.full_name_tokens = " ".split(self.full_name)
		self.base_name_tokens = " ".split(self.base_name) if self.base_name else []

	def strip_punctuation(self, text):
		strip_re = "[^A-Za-z]*(?P<name>.*?)[^A-Za-z]*$"
		return(re.sub(strip_re, lambda x: x.group("name"), text) if text else None) #Remove trailing punctuation and spaces
		
	def strip_non_full_stop(self, text):
		strip_re = "[^A-Za-z]*(?P<name>.*?)[^A-Za-z\.]*$"
		return(re.sub(strip_re, lambda x: x.group("name"), text) if text else None) #Remove trailing punctuation and spaces

	def add_mention(self, name_object):
		self.title = self.title or name_object.title
		self.first_name = self.first_name or name_object.first_name
		self.middle_name = self.middle_name or name_object.middle_name
		self.initials = self.initials or name_object.initials 
		self.surname = self.surname or name_object.surname
		self.set_base_name()
		self.mentions += name_object.mentions
		self.variants += name_object.variants

if __name__ == "__main__":
	print(name_regex)
	#print(first_name_regex)
	
