import json


with open("data/dracula_wiki_plot_entities.txt","r") as f:
    entities_dict = json.load(f)


with open("data/narrQA_questions_formatted_spacy.txt") as f:
    questions = set(f.readlines())

print(entities_dict)
out_list = list()
for quest in questions: #for each question format
    #print(quest)
    
    permu_list = [quest]
    for perms in permu_list:
        #print(perms)
        for word in perms.split(): #examine each word in the question
            word_f = word.strip("$")
            if word_f in entities_dict.keys(): #find if the word is an entity tag
                for entities in entities_dict[word_f]:
                    quest_new = perms.replace(word,entities,1)
                    #print("    ",quest_new)
                    if quest_new not in permu_list:
                        permu_list.append(quest_new)

       #print(permu_list)
    for perms in permu_list:
        if "$" not in perms:
            out_list.append(perms)

print(out_list)

with open("data/questions_drac_spacy.txt","w") as f:
    f.writelines(out_list)

