import os
import os.path as op
import sys

import torch
import datetime
import transformers
from transformers import DistilBertTokenizer, DistilBertForQuestionAnswering
import tensorflow as tf
from qa.question_answering.models.model import Model
from qa.question_answering.utils import get_line_list_from_file

try:
    mimir_dir = os.environ["MIMIR_DIR"]
except KeyError:
    print('Please set the environment variable MIMIR_DIR')
    sys.exit(1)


def file_path_to_text(file):
    line_list = get_line_list_from_file(file)
    raw_text = " ".join([line.strip("\n") for line in line_list])
    return (raw_text)


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


class DistilBertSquadNQA(Model):
    def __init__(self, *args, **kwargs):
        print("we are initializing distilbert")
        super().__init__(*args, **kwargs)
        self.model_id = 'distilbert-squad-nqa'
        model_dir = 'qa/question_answering/models/' + self.model_id
        self.model = DistilBertForQuestionAnswering.from_pretrained(model_dir)
        self.model.to(device)
        self.tokenizer = DistilBertTokenizer.from_pretrained(model_dir)
        print("initialized")

    def answer_question(self, question, context):
        encodings = self.tokenizer(question, context, truncation='only_second', padding='max_length', return_tensors='pt')
        inputs = encodings['input_ids'].reshape(-1).to(device)
        tokens = self.tokenizer.convert_ids_to_tokens(inputs.tolist())
        #print('inputs:', inputs[:10])
        #print('tokens:', tokens[:10])

        outputs = self.model(inputs.reshape(1,-1))
        #print('outputs:', outputs[0][0][:10])
        start_scores = outputs.start_logits.reshape(-1)
        end_scores = outputs.end_logits.reshape(-1)
        #print('start_scores:', start_scores[:10])
        #print('end_scores:', end_scores[:10])

        answer_start = torch.argmax(start_scores)
        #print('answer_start:', answer_start)
        answer_end = answer_start + torch.argmax(end_scores[answer_start:])
        #print('answer_end:', answer_end)
        answer_tokens = tokens[answer_start:answer_end + 1]
        #print('answer_tokens:', answer_tokens)

        answer = self.subword_to_whole_word(answer_tokens)
        if answer == "[CLS]" or answer == "[SEP]":
            return None

        return answer

    def subword_to_whole_word(self, tokens):

        if len(tokens) == 0:
            return ("")

        answer = tokens[0]

        # Select the remaining answer tokens and join them with whitespace.
        for i in range(1, len(tokens)):
            # If it's a subword token, then recombine it with the previous token.
            if len(tokens[i]) >= 2 and tokens[i][0:2] == '##':
                answer += tokens[i][2:]
            # Otherwise, add a space then the token.
            else:
                answer += ' ' + tokens[i]

        return (answer)

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

    def preprocess(self, question):
        return question


if __name__ == "__main__":
    bb = DistilBertSquadNQA("distilbert-squad-nqa")
    import pdb;

    pdb.set_trace()

