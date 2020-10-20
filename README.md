# Mimir (Mini Project)
_Context:_ you are reading a bulky novel, or a biography, or indeed
anything that has a complicated story to tell.
_Challenge:_ design, build and evaluate software capable of
answering questions such as:

* 'remind me who Ivan is' or
* 'How is Ivan related to Petrula?' or
* 'Was it Ivan who met Molotov in Moscow?’

The reader’s questions will be input by voice, because you don't want
to have to look away from the book and certainly not to type
anything. The Companion will speak its answers.

## Requirements
### Speech Recognition
Uses Vosk pip package, and model directories in 'speech_recognition/models'
    pip install vosk 


## Running 
Run test_microphone.py:
    python3 test_microphone.py models/model-directory-here