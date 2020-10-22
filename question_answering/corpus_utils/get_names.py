import nltk, sys 



def download_models():
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('maxent_ne_chunker')
    nltk.download('words')
def get_tokens_from_text(file):

    with open(file) as f:
        file_lines = f.read()

    tokens = nltk.word_tokenize(file_lines)
    
    return tokens

def get_named_entities(tokens):
    entities = nltk.chunk.ne_chunk(nltk.pos_tag(tokens))
    return entities

download_models()
t = get_tokens_from_text(sys.argv[1])
en = get_named_entities(t)

entity_list = list()

for l in en:
    if len(l) == 1:
        #print(l.label())
        #print(l[0][1])
        if "%s (%s)" % ( l[0][0], l.label() ) not in entity_list:
            entity_list.append("%s (%s)" % ( l[0][0], l.label() ) )


print(entity_list)