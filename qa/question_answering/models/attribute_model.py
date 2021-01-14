from qa.question_answering.models.model import Model

class AttributeModel(Model):
	def __init__(self, *args, **kwargs):
		print("we are initializing bert baseline")
		super().__init__(*args, **kwargs)

	def answer_question(self, question, word2entity, obj_dict, attribute = None):
		"""Replaces named entities in a string with their NE type.
		We do not in fact use any NE algorithm here, just the lists of entities 
		that have been found by running NER over texts"""
		
		question = question.lower()

		nes_longest_first = sorted(word2entity.keys(), key = lambda x: len(x), reverse=True)

		for ne in nes_longest_first:
			if ne.lower() in question:
				for ne_class, sub_dict in obj_dict.items():
					if word2entity[ne] in sub_dict:
						entity_object = sub_dict[word2entity[ne]]
						return(entity_object.subnames.get(attribute,None))
		
		return("Not found") #Should be unreachable state
