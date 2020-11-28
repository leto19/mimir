import nltk, sys 


def download_models():
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('maxent_ne_chunker')
    nltk.download('words')

def get_line_list_from_file(file):
    with open(file) as f:
        line_list = f.readlines()
    
    return line_list

def get_tokens_from_text(line):
    tokens = nltk.word_tokenize(line)
    
    return tokens

def get_named_entities(tokens):
    entities = nltk.chunk.ne_chunk(nltk.pos_tag(tokens))
    return entities

download_models()

line_list = get_line_list_from_file(sys.argv[1])
print(line_list)
entity_list = list()
for line in line_list: #for each sentence in the input file 
    print(line)
    line.strip("\n")
    t = get_tokens_from_text(line) #get tokens 
    entities = get_named_entities(t) # get entities tree
    
    for l in entities:
        if len(l) == 1: #it's an entity
            if "%s (%s)" % ( l[0][0], l.label().lower() ) not in entity_list: #if it's not in the list
                entity_list.append("%s (%s)" % ( l[0][0], l.label().lower() ) )
print(entity_list)
print(entities)
import pdb; pdb.set_trace()
