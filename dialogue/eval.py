import csv, sys, os, re, random
from src import StateMachine, States, STATE_TRANSITIONS, TRANSITIONS, DialogueOption

try:
  global mimir_dir
  mimir_dir = os.environ["MIMIR_DIR"]
except KeyError:
  print('Please set the environment variable MIMIR_DIR')
  sys.exit(1)


affirm_words = ['yes', 'correct', 'certainly', 'it is', 'aye']
deny_words = ['no', 'nope', 'it is not', "it isn't", "that's not it" ]


# utils 
def test_exit_command(DSM):
  # -> end
  t = DSM.process_input("exit")
  exit_recognised = False
  if t.dst == States.END:
    exit_recognised = True
  return exit_recognised

def pf(test):
  print('-'*40)
  test()

def get_to_state(state):
  DSM = StateMachine(States, TRANSITIONS, States.ENTRY, States.ANY)
  t = DSM.init_trans()
  if state == States.ENTRY:
    return DSM
  t = DSM.process_input("White Fang")
  if state == States.CONFIRM_BOOK:
    return DSM
  t = DSM.process_input("yes")
  if state == States.NEUTRAL:
    return DSM
  t = DSM.process_input("who is the main character?")
  return DSM


def test_entry():
  '''
  Test the entry state. Possible transitions:
  - self
  - confirm_book
  - exit
  '''
  print("### TESTING ENTRY STATE ###")

  # -> confirm book
  with open(mimir_dir + 'data/nqa_gutenberg_corpus/supported_books.csv', 'r') as file:
    supported_books = list(csv.reader(file))[1:] # [0] is title, [1] is author
      
    nqa_correct = 0
    
    for book_info in supported_books:
      title = book_info[0]
      DSM = StateMachine(States, TRANSITIONS, States.ENTRY, States.ANY)
      t = DSM.init_trans()
      t = DSM.process_input(title)

      if t.dst == States.CONFIRM_BOOK and (title in t.response()):
        nqa_correct += 1

    print("NarrativeQA train set accuracy: {}%".format(nqa_correct/len(supported_books)*100))

  # -> end
  DSM = StateMachine(States, TRANSITIONS, States.ENTRY, States.ANY)
  t = DSM.init_trans()
  is_exiting = test_exit_command(DSM)
  print("Exit command recognised: {}".format(is_exiting)) 


def test_confirm_book():
  '''
  Test the confirm_book state. Possible transitions:
  - self
  - entry
  - exit
  - neutral
  '''
  print("### TESTING CONFIRM BOOK STATE ###")
  state = States.CONFIRM_BOOK

  # -> self
  self_correct = 0
  for word in deny_words:
    DSM = get_to_state(state)
    t = DSM.process_input(word)

    if t.dst == state:
      self_correct += 1
  
  print("Reject book accuracy: {}%".format(self_correct/len(deny_words)*100))

  # -> neutral
  neutral_correct = 0
  for word in affirm_words:
    DSM = get_to_state(state)
    t = DSM.process_input(word)

    if t.dst == States.NEUTRAL:
      neutral_correct += 1
  
  print("Accept book accuracy: {}%".format(neutral_correct/len(affirm_words)*100))

  # -> end
  DSM = get_to_state(States.CONFIRM_BOOK)
  is_exiting = test_exit_command(DSM)
  print("Exit command recognised: {}".format(is_exiting))


def test_neutral():
  '''
  Test the neutral state. Possible transitions:
  - self
  - answer
  - exit
  '''
  print("### TESTING NEUTRAL STATE ###")
  state = States.NEUTRAL
  # -> answer
  # q_correct = 0
  # with open(mimir_dir + 'data/narrQA_question_sample.txt', 'r') as file:
  #   questions = file.read().split("\n")
  #   for q in questions:
  #     DSM = get_to_state(state)
  #     t = DSM.process_input(q)
      
  #     if t.dst == States.ANSWER:
  #       q_correct += 1
  #     else:
  #       print(q)
  #   print("NarrativeQA question sample accuracy: {}%".format(q_correct/len(questions)*100))

  q_correct = 0
  a_correct = 0

  wrong_qs = []
  wrong_as = []
  with open(mimir_dir + 'data/narrativeqa_qas.csv', 'r') as file:
    test_rows = list(csv.reader(file))[1:]
    random.Random(0).shuffle(test_rows)
    test_rows = test_rows[:100]

    for row in test_rows:
      # test question
      DSM = get_to_state(state)
      q = row[2]
      t = DSM.process_input(q)
      if t.dst == States.ANSWER:
        q_correct += 1
      else:
        wrong_qs.append((q, t.dst))

      # test answer
      DSM = get_to_state(state)
      a = row[3]
      t = DSM.process_input(a)
      if t.dst == state:
        a_correct += 1
      else:
        wrong_as.append((a, t.dst))
    
    print("NQA question classification accuracy: {}%".format(q_correct/len(test_rows)*100))
    print("NQA non-question classification accuracy: {}%".format(a_correct/len(test_rows)*100))
    print("Overall accuracy: {}%".format((q_correct + a_correct)/(len(test_rows)*2)*100))

  print("Incorrectly classified questions: ", wrong_qs)    
  print("Incorrecly classified answers: ", wrong_as)

  # -> end
  DSM = get_to_state(state)
  is_exiting = test_exit_command(DSM)
  print("Exit command recognised: {}".format(is_exiting))


def test_answer():
  '''
  Test the neutral state. Possible transitions:
  - self
  - neutral
  - exit
  '''
  print("### TESTING ANSWER STATE ###")
  state = States.ANSWER

  
  # -> self
  q_correct = 0
  with open(mimir_dir + 'data/narrQA_question_sample.txt', 'r') as file:
    questions = file.read().split("\n")
    for q in questions:
      DSM = get_to_state(state)
      t = DSM.process_input(q)
      
      if t.dst == state:
        q_correct += 1

    print("NarrativeQA question sample accuracy: {}%".format(q_correct/len(questions)*100))


  # -> end
  DSM = get_to_state(States.ANSWER)
  is_exiting = test_exit_command(DSM)
  print("Exit command recognised: {}".format(is_exiting))


if __name__ == '__main__':

  #print(re.match("(who|what|where|when|how|why|whose|who's)", "In what year does Adam's wife become ill?"))
  pf(test_entry)
  pf(test_confirm_book)
  pf(test_neutral)
  pf(test_answer)