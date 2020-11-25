import re 

class DialogueStateMachine():
  def __init__(self, states, transitions, start_state, end_states):
    self.states = states
    self.transitions = transitions
    self.current_state = start_state
    self.end_states = end_states
    self.state_history = []
    self.boldPrint("Hello, what book are you reading today?")


  def boldPrint(self, text):
    '''
    Prints to console in bold text, used for system responses.
    '''
    print('\033[1m' + text + '\033[0m')


  def get_repeat_transition(self):
    '''
    Returns a self-loop transition into the current state, used when
    no other transition condition is met. 
    '''
    return {
      "src": self.current_state,
      "dst": self.current_state,
      "condition": None,
      "response": lambda: "Sorry, I don't understand."
    }

  def trans_state(self, transition):
    '''
    Transitions from one state to another. Returns false if the state is an end
    state, true otherwise.
    '''
    self.state_history.append(self.current_state)
    self.current_state = transition['dst']
    self.boldPrint(transition['response']())
    print("***{}***".format(transition['dst']))

    if self.current_state in self.end_states:
      print("[DIALOGUE OVER]")
      return False

    return True

  def process_input(self, text_in):
    '''
    Processes a user input, transitioning to a new state if any condition is met.
    Returns false if the state is an end state, true otherwise.
    '''
    poss_transitions = [t for t in self.transitions if t['src'] == self.current_state]

    for t in poss_transitions:
      if t['condition'](text_in):
        return self.trans_state(t)
    
    return self.trans_state(self.get_repeat_transition())
