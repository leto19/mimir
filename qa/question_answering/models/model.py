class Model:
    def __init__(self, model_id: str):
        self.model_id = model_id

    def answer_question(self, question, data):
        raise NotImplementedError

    def preprocess(self, question):
        raise NotImplementedError
