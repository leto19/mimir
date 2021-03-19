
class BertBaseline(Model):
	def __init__(self, model_id):
		print("we are initializing bert baseline")
		Model.__init__(self, model_id)
		#self.valid_dir= valid_dir=op.join(mimir_dir,"data","nqa_summary_text_files","valid")
		#self.valid_files=sorted(os.listdir(valid_dir))
		self.model_id = 'distilbert-base-uncased-distilled-squad'
#		self.model_id = 'bert-large-uncased-whole-word-masking-finetuned-squad'
	#	self.cache_dir = op.join(mimir_dir,"question_answering","qa_models") 
		print("bert model")
		self.bert_model = DistilBertForQuestionAnswering.from_pretrained(self.model_id)
		print("bert model to device")
		self.bert_model.to(device)
		print("self.tokenizer")
		self.tokenizer = DistilBertTokenizer.from_pretrained(self.model_id)
		print("initialized")
