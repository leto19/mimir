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
All Python package and model requriements can be satisified by running the installer BASH script, ```install.sh```


## Usage

Program can be run using ```./mimir``` after installation. The following command line options are available:
- ```-g```, ```--google``` - use Google API for ASR (slower but more accurate)
- ```-d```, ```--distilbert``` - use Distilbert for QA (default is T5)
- ```-s```, ```--silent``` - Don't use ASR or TTS 