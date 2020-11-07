# Runs the dialogue system using the command line for input/output
from state_machine import DialogueStateMachine
from config import STATES, TRANSITIONS

if __name__ == '__main__':
  # Create State-based dialogue instance
  dsm = DialogueStateMachine(STATES, TRANSITIONS, STATES[0], STATES[-1])

  persist_dialogue = True

  # While not in end_state, keep running
  while persist_dialogue:
    user_input = input("> ")
    persist_dialogue = dsm.process_input(user_input.lower())
