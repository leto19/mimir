import sys
import spacy
#from spacy import displacy
#from collections import Counter
import en_core_web_sm
nlp = en_core_web_sm.load()

"""
Takes a file containing a list of questions as an argument, and replaces any named entities
detected in each question with a $ tag.
e.g. "Who is Johnathan" -> "Who is $NAME"
"""

def get_line_list_from_file(file):
    with open(file) as f:
        line_list = f.readlines()
    
    return line_list

line_list = get_line_list_from_file(sys.argv[1])
#print(line_list)
quest_list = list()
for line in line_list: #for each question in the input file 
    line.strip("\n")
    line = line.replace("?","") #formatting
    entities = nlp(line).ents #get named entities 
    print(line)
    print(entities)
    for e in entities: # for each entity in the question
        e_label = "$"+str(e.label_).upper() #format the tag
        line = line.replace(e.text,e_label) # replace the entity in the question with tag
    quest_list.append(line) 

quest_list = list(filter(None,quest_list))
print(quest_list)

with open("data/narrQA_questions_formatted_spacy.txt","w+") as f:
    f.writelines(quest_list)

