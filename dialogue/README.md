## Dialogue System

Currently a very simple finite-state machine system for controlling a dialogue (proof of concept). Within the system there are a number of pre-defined *states*, which the user traverses via pre-defined *transitions* (see `config.py` file). A transition is made subject to its defined condition, which currently a combination of regex-based and embedding similarity-based (the latter making use of the cosine similarity of the sentence embedding of the user utterance and the sentence embedding of a 'model answer' for that transition.

***
### Running the system:
Navigate to this sub-directory via the command line and run:
```python
python run_cl.py
```

***
### Authors:
* **Tomas Goldsack**
