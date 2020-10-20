# Mimir (Mini Project)
__Context:__ you are reading a bulky novel, or a biography, or indeed anything that has a complicated story to tell.

__Challenge:__ design, build and evaluate software capable of
answering questions such as:

* 'remind me who Ivan is' or
* 'How is Ivan related to Petrula?' or
* 'Was it Ivan who met Molotov in Moscow?’

The reader’s questions will be input by voice, because you don't want
to have to look away from the book and certainly not to type
anything. The Companion will speak its answers.

## Requirements
### Speech Recognition
Uses Vosk pip package
```
pip install vosk 
```
model directories go in 'speech_recognition/models'

[Models for Vosk can be obtained here](https://alphacephei.com/vosk/models)

## Running 
Run test_microphone.py:
```    
python3 test_microphone.py models/model-directory-here
```