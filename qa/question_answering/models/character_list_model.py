from qa.question_answering.models.model import Model

class CharacterListModel(Model):
	def __init__(self, *args, **kwargs):
		print("we are initializing bert baseline")
		super().__init__(*args, **kwargs)
	

	def answer_question(self, _, obj_dict, n=4):
		"""Replaces named entities in a string with their NE type.
		We do not in fact use any NE algorithm here, just the lists of entities 
		that have been found by running NER over texts"""

		characters = obj_dict["PERSON"]

		chars_sorted = sorted(characters, key = lambda x: len(x.sents), reverse=True)

		full_names = [max(obj.name_variants, key = lambda x: len(x)) for obj in chars_sorted] 		

		return(full_names[:n])

