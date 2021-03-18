import tensorflow as tf
from .models import InferSent
import torch
import numpy as np

# Define classes
# ['DESC', 'LOC', 'HUM', 'ENTY', 'ABBR', 'NUM']
cls_dict = {
  'DESC': 0,
  'LOC': 1,
  'HUM': 2,
  'ENTY': 3,
  'ABBR': 4,
  'NUM': 5
}

class QuestionClassifier():
  def __init__(self):
    xtrain = []

    with open("./data/question_classification/trec_train.txt", 'rb') as f:
      questions = [x.decode('utf8').strip() for x in f.readlines()]
      for q in questions:
          splt = q.replace("\n", "").split(":")
          xtrain.append(" ".join(splt[1].split(" ")[1:]))

    V = 2
    MODEL_PATH = './dialogue/models/encoder/infersent%s.pkl' % V
    params_model = {'bsize': 64, 'word_emb_dim': 300, 'enc_lstm_dim': 2048,
                    'pool_type': 'max', 'dpout_model': 0.0, 'version': V}

    self.infersent = InferSent(params_model)
    self.infersent.load_state_dict(torch.load(MODEL_PATH))

    W2V_PATH = './dialogue/models/fastText/crawl-300d-2M.vec'
    self.infersent.set_w2v_path(W2V_PATH)

    self.infersent.build_vocab(xtrain, tokenize=True)

    print("Infersent built")

    #self.model = tf.keras.models.load_model('./dialogue/models/rnn_model')
    #print(self.model.summary())
    self.model = tf.saved_model.load('./models/qc_rnn_model')

    print("RNN Model loaded")


  def classify(self, question_text):
    enc_q = self.infersent.encode(np.array([question_text]), tokenize=True)
    reshaped = np.array([x.reshape(1, 4096) for x in enc_q])
    tf_test = tf.convert_to_tensor(reshaped)
    print(tf_test.shape)
    pred = self.model(tf_test)
    return np.argmax(pred)