## Dialogue System

Currently a very simple finite-state machine system for controlling a dialogue (proof of concept). Within the system there are a number of pre-defined *states*, which the user traverses via pre-defined *transitions* (see `config.py` file). A transition is made subject to its defined condition, which currently a fragile simple regex-based system.

These conditions will soon evolve into a more robust (likely probability-based) system for determining user intent, and addional states will be added.

***
### Running the system:
Navigate to this sub-directory via the command line and run:
```python
python run_cl.py
```

***
### Authors:
* **Tomas Goldsack**