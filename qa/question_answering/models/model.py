from qa.question_answering.models import *


mimir_dir = os.environ["MIMIR_DIR"]


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
        with open('active_models.txt', 'r') as active_models_file:
            for line in active_models_file:
                model_id, class_name = line.split(',')
                self.models_dict[model_id, globals()[class_name](model_id)]
        self.current_book = None
        self.current_sumary = None
        self.current_text = None

    def confirm_book(self, book_id):
        self.current_book = book_id
        self.current_summary = open(mimir_dir + '/data/nqa_summary_text_files/train' + 'book_id'.read())
        self.current_text = open(mimir_dir + '/data/nqa_gutenberg_corpus/train' + 'book_id'.read())

    def answer_question(self, model_id, question):
        model = self.models_dict.get(model_id)
        answer = model.answer_question(question, self.current_sumary)
        return answer


