import re 

class DialogueStateMachine():
  def __init__(self, states, transitions, start_state, end_states):
    self.states = states
    self.transitions = transitions
    self.current_state = start_state
    self.end_states = end_states
    self.state_history = []
    print("Hello, what book are you reading today?")

  def get_repeat_transition(self):
    return {
      "src": self.current_state,
      "dst": self.current_state,
      "condition": None,
      "response": lambda: "Sorry, I did not understand."
    }

  def trans_state(self, transition):
    self.state_history.append(self.current_state)
    self.current_state = transition['dst']
    print(transition['response']())
    print("***{}***".format(transition['dst']))

    if self.current_state in self.end_states:
      print("[DIALOGUE OVER]")
      return False

    return True

  def process_input(self, text_in):
    poss_transitions = [t for t in self.transitions if t['src'] == self.current_state]

    for t in poss_transitions:
      if t['condition'](text_in):
        return self.trans_state(t)
    
    return self.trans_state(self.get_repeat_transition())
