from qa.question_answering.models.model import Model

class CharacterListModel(Model):
	def __init__(self, *args, **kwargs):
		print("we are initializing bert baseline")
		super().__init__(*args, **kwargs)
	

	def answer_question(self, _, ne_mentions, obj_dict, n=4):
		"""Replaces named entities in a string with their NE type.
		We do not in fact use any NE algorithm here, just the lists of entities 
		that have been found by running NER over texts"""
		mentions_list = [mention[1][1] for mention in ne_mentions]
		#mentions_list = [l for s in mentions_list for l in s]

		characters = obj_dict["PERSON"]
		names = [(ind, max(char.name_variants, key=lambda x: len(x))) for ind, char in characters.items()]
	
		n_mentions = [len([ment for ment in mentions_list if ment == name[0]]) for name in names]

		results = list(zip([name[1] for name in names], n_mentions))
	
		results = sorted(results, key = lambda x: x[1], reverse=True)

		return([r[0] for r in results][:n])

