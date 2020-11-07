import os
import os.path as op
import pandas as pd
import torch
import time
import numpy as np
import datetime
from torch.utils.data import TensorDataset, DataLoader, SequentialSampler
import transformers
from transformers import AutoTokenizer, AutoModelForQuestionAnswering, BertForQuestionAnswering, BertTokenizer
import tensorflow as tf
from qa_models.utils import file_path_to_text

mimir_dir = os.environ["MIMIR_DIR"]

def format_time(elapsed):
  elapsed_rounded = int(round(elapsed))
  return str(datetime.timedelta(seconds=elapsed_rounded))


if torch.cuda.is_available():
	device = torch.device('cuda')
	print('There are %d GPU(s) available.' % torch.cuda.device_count())
	device_name = tf.test.gpu_device_name()
	print('We will use the GPU:'.format(device_name))
else:
	print('No GPU available, using CPU instead')
	device = torch.device('cpu')

class BertBaseline():
	def __init__(self, valid_dir=op.join(mimir_dir,"data","nqa_summary_text_files","valid")):
		print("we are initializing bert baseline")
		self.valid_dir=valid_dir
		self.valid_files=sorted(os.listdir(valid_dir))
		self.model_id = 'bert-large-uncased-whole-word-masking-finetuned-squad'
		self.cache_dir = op.join(mimir_dir,"question_answering","qa_models") 
		print("bert model")
		self.bert_model = BertForQuestionAnswering.from_pretrained(self.model_id, cache_dir=self.cache_dir)
		print("bert model to device")
		self.bert_model.to(device)
		print("self.tokenizer")
		self.tokenizer = BertTokenizer.from_pretrained(self.model_id, cache_dir=self.cache_dir)
		print("initialized")
	
	def evaluate_question(self, question, summary_file_path):
	
		context = file_path_to_text(summary_file_path)
		input_ids = self.tokenizer.encode(question, context, truncation='only_second')
		tokens = tokenizer.convert_ids_to_tokens(input_ids)

		start_scores, end_scores = model(torch.tensor([input_ids]),
										 token_type_ids=torch.tensor([token_type_ids]))
		answer_start = torch.argmax(start_scores)
		answer_end = torch.argmax(end_scores)
		answer_tokens = tokens[answer_start:answer_end+1]
		
		answer = self.subword_to_whole_word(answer_tokens)
		
		return(answer)


	def subword_to_whole_word(self, tokens):

		answer = tokens[0]		

		# Select the remaining answer tokens and join them with whitespace.
		for i in range(1,len(answer)):
			# If it's a subword token, then recombine it with the previous token.
			if tokens[i][0:2] == '##':
				answer += tokens[i][2:]
			# Otherwise, add a space then the token.
			else:
				answer += ' ' + tokens[i]
		
		return(answer)

	def print_tokens(self, tokens, input_ids):

		# For each token and its id...
		for i, (token, id) in enumerate(zip(tokens, input_ids)):
			if i == 32: break

			# If this is the [SEP] token, add some space around it to make it stand out.
			if id == tokenizer.sep_token_id:
				print('')
			
			# Print the token string and its ID in two columns.
			print('{:<12} {:>6,}'.format(token, id))

			if id == tokenizer.sep_token_id:
				print('')

