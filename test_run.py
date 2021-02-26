# Runs the dialogue system using the command line for input/output

from dialogue import init_dialogue, dialogue_input, DialogueOption, bold_print


if __name__ == '__main__':

  persist_dialogue = True
  # Initialise dialogue + other components
  ret = init_dialogue()
  bold_print(ret["response"])

  # While not in end_state, keep running
  while persist_dialogue:

    #user_input = sr.get_input_string() # returns string
    user_input = input("> ")
    
    ret = dialogue_input(user_input)
    dialogue_id = ret['id']

    response = None 

    if dialogue_id == DialogueOption.EXIT:
      persist_dialogue = False

    elif dialogue_id == DialogueOption.DA_RESPONSE:
      response = ret['response']

    elif dialogue_id == DialogueOption.BOOK_CONFIRMED:
      response = ret['response']

    elif dialogue_id == DialogueOption.QA_RESPONSE:
      response = "answer"

    bold_print(response)
    