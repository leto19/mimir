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
#print(line_list)
entity_dict = dict()
quest_list = list()
for line in line_list: #for each sentence in the input file 
    #print(line)
    line.strip("\n")
    t = get_tokens_from_text(line) #get tokens 
    entities = get_named_entities(t) # get entities tree
    q_string_list = list()
    for element in entities:
        if type(element) is nltk.tree.Tree:
            print(element.label())
            ent_label = element.label()
            ent_name = element.leaves()[0][0]
           
            if ent_label not in entity_dict.keys():
                entity_dict[ent_label] = [ent_name]
            else:
                entity_dict[ent_label].append(ent_name)
            q_string_list.append("$%s"%ent_label)
        else:
            q_string_list.append(element[0])
        print(q_string_list)
    q_string_list += "\n"
    q_string = " ".join(q_string_list)
    if "$" in q_string:
        quest_list.append(q_string)
quest_list = list(filter(None,quest_list))

with open("data/narrQA_questions_formatted.txt","w+") as f:
    f.writelines(quest_list)
print(entity_dict['GPE'])
print(quest_list)