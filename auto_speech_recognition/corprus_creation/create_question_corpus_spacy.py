import json
import sys

with open(sys.argv[1],"r") as f:
    entities_dict = json.load(f)


with open("data/survey_qs_formatted.txt") as f:
#with open("data/quest_format.txt") as f:
    questions = set(f.readlines())

print(entities_dict)
out_list = list()
out_list.append(sys.argv[1].replace("_entities.txt","").replace("data/asr_entity_files/","")+"\n")

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
with open("data/question_files2/%s_questions.txt"%sys.argv[1].replace("_entities.txt","").replace("data/asr_entity_files/",""),"w") as f:
    f.writelines(out_list)

