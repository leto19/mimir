import re 
from .config import Transition, DialogueOption

class StateMachine():
  def __init__(self, states, transitions, start_state, any_state):
    self.states = states
    self.transitions = transitions
    self.start_state = start_state
    self.current_state = None
    self.any_state = any_state
    self.state_history = []
    # run initialise transition

  def init_trans(self):
    '''
    Performs a transition into the intial state (if there is one)
    '''
    t = [t for t in self.transitions if t.src == None and t.dst == self.start_state][0]
    return self.trans_state(t)


  def get_repeat_transition(self):
    '''
    Returns a self-loop transition into the current state, used when
    no other transition condition is met. 
    '''
    return Transition(
      self.current_state,
      self.current_state,
      DialogueOption.DA_RESPONSE,
      None,
      "Sorry, I don't understand."
    )

  def trans_state(self, transition):
    '''
    Transitions from one state to another. Returns false if the state is an end
    state, true otherwise.
    '''
    self.state_history.append(self.current_state)
    self.current_state = transition.dst
    print(transition)
    return transition

  def process_input(self, text_in):
    '''
    Processes a user input, transitioning to a new state if any condition is met.
    Returns false if the state is an end state, true otherwise.
    '''
    poss_transitions = [t for t in self.transitions if 
      (t.src == self.current_state or t.src == self.any_state)]

    for t in poss_transitions:
      if t.condition(text_in):
        return self.trans_state(t)
    
    return self.trans_state(self.get_repeat_transition())
