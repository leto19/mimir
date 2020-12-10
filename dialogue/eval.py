import csv, sys, os
from dialogue.state_machine import StateMachine
from dialogue.config import States, STATE_TRANSITIONS, TRANSITIONS, DialogueOption


try:
  global mimir_dir
  mimir_dir = os.environ["MIMIR_DIR"]
except KeyError:
  print('Please set the environment variable MIMIR_DIR')
  sys.exit(1)


def test_entry():
  '''
  Test the entry state. Possible transitions:
  - self
  - confirm_book
  - exit
  '''

  # -> confirm book
  with open(mimir_dir + 'data/nqa_gutenberg_corpus/supported_books.csv', 'r') as file:
    supported_books = list(csv.reader(file))[1:] # [0] is title, [1] is author
      
    nqa_correct = 0
    
    for title, author in zip(*supported_books):
      DSM = StateMachine(States, TRANSITIONS, States.ENTRY, States.ANY)
      t = DSM.init_trans()
      t = DSM.process_input(title)
      if t.dst == States.CONFIRM_BOOK:
        nqa_correct += 1

    print("NarrativeQA books recognised: {}%".format(nqa_correct/len(supported_books)*100))
  


def test_confirm_book(print=False):
  '''
  Test the confirm_book state. Possible transitions:
  - self
  - entry
  - exit
  - neutral
  '''    

  return


def test_neutral(print=False):
  '''
  Test the neutral state. Possible transitions:
  - self
  - answer
  '''
  return


def test_answer(print=False):
  '''
  Test the neutral state. Possible transitions:
  - self
  - neutral
  '''
  return


if __name__ == '__main__':
  test_entry()