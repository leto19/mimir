import re 

class DialogueStateMachine():
  def __init__(self, states, transitions, start_state, end_states, is_clarify = True):
    self.states = states
    self.transitions = transitions
    self.current_state = start_state
    self.end_states = end_states
    self.is_clarify = is_clarify
    print("Hello, what can I help you with?")

  def get_clarify_transition(self):
    return {
      "src": self.current_state,
      "dst": self.current_state,
      "condition": None,
      "response": "Sorry, I did not understand."
    }

  def trans_state(self, transition):
    self.current_state = transition['dst']
    print(transition['response'])
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
    
    return self.trans_state(self.get_clarify_transition()) if self.is_clarify else False
    
    
