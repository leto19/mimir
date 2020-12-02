import speech_recognition.get_speech_input as sr

if __name__ == '__main__':
  persist_dialogue = True

  # Initialise dialogue

  # While not in end_state, keep running
  while persist_dialogue:

    user_input = sr.get_input_string() # return string
    
    # pass user input to dialogue, which returns a response or something signifying QA comp is needed (or user has chosen to exit)

    # if QA comp is needed, get response from QA system

    # use TTS component to read response out
