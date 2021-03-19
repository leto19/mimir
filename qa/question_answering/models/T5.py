import os
import os.path as op
import sys
import torch
import datetime
import transformers
from transformers import T5Tokenizer, T5ForConditionalGeneration
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


class T5(Model):
    def __init__(self, *args, **kwargs):
        print("we are initializing T5")
        super().__init__(*args, **kwargs)
        self.model_id = 'T5'
        model_dir = './models/' + self.model_id
        self.model = T5ForConditionalGeneration.from_pretrained(model_dir)
        self.model.to(device)
        self.tokenizer = T5Tokenizer.from_pretrained(model_dir)
        print("initialized")

    def answer_question(self, question, context):
        question_input_ids = tokenizer.encode('question: ' + q + '\t' + 'context: ' + c, max_length=1024, padding='max_length', truncation=True, return_tensors='pt')
        input_ids = torch.tensor(question_input_ids).to(device)

        output_ids = self.model.generate(input_ids,
                                    num_beams=4,
                                    no_repeat_ngram_size=2,
                                    min_length=2,
                                    max_length=50,
                                    early_stopping=False)

        answer = self.tokenizer.decode(output_ids, skip_special_tokens=True)

        return answer


if __name__ == "__main__":
    bb = T5("T5")
    import pdb;

    pdb.set_trace()

