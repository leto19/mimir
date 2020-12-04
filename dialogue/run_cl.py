# Runs the dialogue system using the command line for input/output
from dialogue.state_machine import StateMachine
from dialogue.config import States, TRANSITIONS, DialogueOption
from dialogue.utils import bold_print


if __name__ == '__main__':
  # Create State-based dialogue instance
  dsm = StateMachine(States, TRANSITIONS, States.ENTRY, States.ANY)
  
  # Perform initial transition
  cs, res = dsm.init_trans()
  bold_print(res)

  persist_dialogue = True

  # While not in end_state, keep running
  while persist_dialogue:
    user_input = input("> ")
    cs, res = dsm.process_input(user_input.lower())
    bold_print(res)

    if (STATE_CODES[cs] == DialogueOption.EXIT):
      persist_dialogue = False
    