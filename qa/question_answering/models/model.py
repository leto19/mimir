import sys
import importlib

from qa.question_answering.models import *
import os

try:
    mimir_dir = os.environ["MIMIR_DIR"]
except KeyError:
    print('Please set the environment variable MIMIR_DIR')
    sys.exit(1)

class Model:
    def __init__(self, model_id: str):
        self.model_id = model_id

    def answer_question(self, question, data):
        raise NotImplementedError

    def preprocess(self, question):
        raise NotImplementedError


class ModelController:
    def __init__(self):
        self.models_dict = {}
        with open('qa/question_answering/models/active_models.txt', 'r') as active_models_file:
            for line in active_models_file:
                model_id, class_location, class_name = line.replace(' ', '').strip().split(',')
                module = importlib.import_module('qa.question_answering.models.'+class_location)
                model = getattr(module, class_name)
                self.models_dict[model_id] = model(model_id)
        self.current_book = None
        self.current_summary = None
        self.current_text = None

    def confirm_book(self, book_id):
        self.current_book = book_id
        self.current_summary = open(mimir_dir + 'data/nqa_summary_text_files/train/' + book_id['title']).read()
        self.current_text = open(mimir_dir + 'data/nqa_gutenberg_corpus/train/' + book_id['title']).read()

    def answer_question(self, model_id, question):
        model = self.models_dict.get(model_id)
        answer = model.answer_question(question, self.current_summary)
        return answer
