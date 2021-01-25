import json
import sys 
import spacy
from spacy import displacy
from collections import Counter
import en_core_web_sm
nlp = en_core_web_sm.load()

"""
Takes a file as an input and returns a writes a dictionary to a file
containing all named entities detected in that file. 
"""


class SetEncoder(json.JSONEncoder):
    def default(self,obj):
        if isinstance(obj,set):
            return list(obj)
        return json.JSONEncoder.default(self,obj)

def get_lines_from_file(file):
    with open(file) as f:
        line_list = f.read()
    return line_list

lines = get_lines_from_file(sys.argv[1])
doc = nlp(lines)
entity_dictionary = dict()
for entity in doc.ents: #build entity dictionary 
    if entity.label_ not in entity_dictionary.keys():
        entity_dictionary[entity.label_] = {entity.text}
    else:
        entity_dictionary[entity.label_].add(entity.text)
print(entity_dictionary)
print(entity_dictionary.keys())

with open("data/asr_entity_files/%s_entities.txt"%(sys.argv[1].replace(".txt","").replace("data/nqa_summary_text_files/train/","")),"w") as f:
    f.write(json.dumps(entity_dictionary,cls=SetEncoder))
