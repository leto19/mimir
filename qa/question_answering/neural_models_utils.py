
def format_time(elapsed):
		'''
		Takes a time in seconds and returns a string hh:mm:ss
		'''
		# Round to the nearest second.
		elapsed_rounded = int(round((elapsed)))

		# Format as hh:mm:ss
		return str(datetime.timedelta(seconds=elapsed_rounded))



def format_data(data):
	contexts = []
	questions = []
	answers = []
	for index, row in data.iterrows():
		context		= row['summary']
		question	= row['question_tokenized']
		answer		= {}
		answer['text'] = row['answer']
		answer['answer_start'] = row['ans_start']

		contexts.append(context)
		questions.append(question)
		answers.append(answer)
	
	return contexts, questions, answers


def add_end_idx(answers, contexts):
    for answer, context in zip(answers, contexts):
        gold_text = answer['text'].strip()
        answer['text'] = gold_text
        start_idx = answer['answer_start']
        end_idx   = start_idx + len(gold_text) - 1
        answer['answer_end'] = end_idx


def tokenize_questions_and_contexts(questions, contexts, tokenizer):

  input_ids       = []
  token_type_ids  = []

  for i in range(len(questions)):
    question_input_ids      = tokenizer.encode(question, context, truncation='only_second',padding='max_length')
    sep_index               = question_input_ids.index(tokenizer.sep_token_id)
    num_tokens_question     = sep_index + 1
    num_tokens_context      = len(q_input_ids) - num_tokens_question
    question_token_type_ids = [0]*num_tokens_question + [1]*num_tokens_context

    input_ids.append(torch.tensor(q_input_ids))
    token_type_ids.append(torch.tensor(question_token_type_ids))
    tokens.append(tokenizer.convert_ids_to_tokens(question_input_ids))

  input_ids       = torch.cat(input_ids, dim=0)
  token_type_ids  = torch.cat(token_type_ids, dim=0)

  return input_ids, token_type_ids


def add_token_positions(encodings, answers):
    start_positions = []
    end_positions   = []

    for i in range(len(answers)):
      char_to_token_start = encodings.char_to_token(i, answers[i]['answer_start'], sequence_index=1)
      char_to_token_end = encodings.char_to_token(i, answers[i]['answer_end'], sequence_index=1)
      
      #input_ids = encodings.input_ids[i]
      #tokens = tokenizer.decode(encodings.input_ids[i])
      #print('input ids:', input_ids)
      #print('tokens:', tokens)
      #print('answer info:', answers[i])
      #print('char_to_token start:', char_to_token_start)
      #print('char_to_token end:', char_to_token_end)
      #print('decoded start token:', tokenizer.decode(input_ids[char_to_token_start]))
      #print('decoded end token:', tokenizer.decode(input_ids[char_to_token_end]))

def format_time(elapsed):
		'''
		Takes a time in seconds and returns a string hh:mm:ss
		'''
		# Round to the nearest second.
		elapsed_rounded = int(round((elapsed)))

		# Format as hh:mm:ss
		return str(datetime.timedelta(seconds=elapsed_rounded))



def format_data(data):
	contexts = []
	questions = []
	answers = []
	for index, row in data.iterrows():
		context		= row['summary']
		question	= row['question_tokenized']
		answer		= {}
		answer['text'] = row['answer']
		answer['answer_start'] = row['ans_start']

		contexts.append(context)
		questions.append(question)
		answers.append(answer)
	
	return contexts, questions, answers


def add_end_idx(answers, contexts):
    for answer, context in zip(answers, contexts):
        gold_text = answer['text'].strip()
        answer['text'] = gold_text
        start_idx = answer['answer_start']
        end_idx   = start_idx + len(gold_text) - 1
        answer['answer_end'] = end_idx


def tokenize_questions_and_contexts(questions, contexts, tokenizer):

  input_ids       = []
  token_type_ids  = []

  for i in range(len(questions)):
    question_input_ids      = tokenizer.encode(question, context, truncation='only_second',padding='max_length')
    sep_index               = question_input_ids.index(tokenizer.sep_token_id)
    num_tokens_question     = sep_index + 1
    num_tokens_context      = len(q_input_ids) - num_tokens_question
    question_token_type_ids = [0]*num_tokens_question + [1]*num_tokens_context

    input_ids.append(torch.tensor(q_input_ids))
    token_type_ids.append(torch.tensor(question_token_type_ids))
    tokens.append(tokenizer.convert_ids_to_tokens(question_input_ids))

  input_ids       = torch.cat(input_ids, dim=0)
  token_type_ids  = torch.cat(token_type_ids, dim=0)

  return input_ids, token_type_ids


def add_token_positions(encodings, answers):
    start_positions = []
    end_positions   = []

    for i in range(len(answers)):
      char_to_token_start = encodings.char_to_token(i, answers[i]['answer_start'], sequence_index=1)
      char_to_token_end = encodings.char_to_token(i, answers[i]['answer_end'], sequence_index=1)
      
      #input_ids = encodings.input_ids[i]
      #tokens = tokenizer.decode(encodings.input_ids[i])
      #print('input ids:', input_ids)
      #print('tokens:', tokens)
      #print('answer info:', answers[i])
      #print('char_to_token start:', char_to_token_start)
      #print('char_to_token end:', char_to_token_end)
      #print('decoded start token:', tokenizer.decode(input_ids[char_to_token_start]))
      #print('decoded end token:', tokenizer.decode(input_ids[char_to_token_end]))

      start_positions.append(char_to_token_start)
      end_positions.append(char_to_token_end)

      # if start position is None, the answer passage has been truncated
      if start_positions[-1] is None:
          start_positions[-1] = tokenizer.model_max_length

      # if end position is None, the 'char_to_token' function points to the space before the correct token - > add + 1
      if end_positions[-1] is None:
        end_positions[-1] = encodings.char_to_token(i, answers[i]['answer_end'] + 1)

      if end_positions[-1] is None:
        end_positions[-1] = tokenizer.model_max_length
      

    encodings.update({'start_positions': start_positions, 'end_positions': end_positions})


      start_positions.append(char_to_token_start)
      end_positions.append(char_to_token_end)

      # if start position is None, the answer passage has been truncated
      if start_positions[-1] is None:
          start_positions[-1] = tokenizer.model_max_length

      # if end position is None, the 'char_to_token' function points to the space before the correct token - > add + 1
      if end_positions[-1] is None:
        end_positions[-1] = encodings.char_to_token(i, answers[i]['answer_end'] + 1)

      if end_positions[-1] is None:
        end_positions[-1] = tokenizer.model_max_length
      

    encodings.update({'start_positions': start_positions, 'end_positions': end_positions})

