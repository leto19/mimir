from qa.question_answering.models.model import Model

class AttributeModel(Model):
	def __init__(self, *args, **kwargs):
		print("we are initializing bert baseline")
		super().__init__(*args, **kwargs)

	def answer_question(self, question, word2entity, obj_dict, attribute = None):
		
		question = question.lower()

		nes_longest_first = sorted(word2entity.keys(), key = lambda x: len(x), reverse=True)

		for ne in nes_longest_first:
			if ne.lower() in question:
				ne_object = word2entity[ne]
				return(ne_object.subnames.get(attribute,None))
		
		return("Not found") #Should be unreachable state
