import nltk
from utils import get_named_entities, tokenize


class SimpleBaseline:
	def __init__(self):
		self.categories = {"PER", #person
						"DES", #personal description
						"LOC", #location
						"ORG", #organization
						"OTH" #other
						}

#	def preprocess_question(self, question):
#		return([stemmer.stem(w) for w in remove_stopwords(tokenize(question))])

	def classify_question(self, question):
		question_tokens = tokenize(question) 
		words_and_labels = get_named_entities(question_tokens)

		entities = [ne for ne in words_and_labels if isinstance(ne, nltk.tree.Tree)]

		labels = [e.label() for e in entities]

		who_condition = "who" in [t.lower() for t in question_tokens]
		whose_condition = "whose" in [t.lower() for t in question_tokens]
		what_condition = "what" in [t.lower() for t in question_tokens]
		where_condition = "where" in [t.lower() for t in question_tokens]
		when_condition = "when" in [t.lower() for t in question_tokens]
		why_condition = "why" in [t.lower() for t in question_tokens]
		how_condition = "how" in [t.lower() for t in question_tokens]
		
		named_person_condition = "PERSON" in labels

		if who_condition and not named_person_condition:
			return("PER") #We want a person's name
			
		if who_condition and named_person_condition:
			return("DES") #We want a person's description

		if where_condition:
			return("LOC") #Location
		
		else:
			return("OTH")
