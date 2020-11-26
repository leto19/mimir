with open("data/entities.txt","r") as f:
    ent = f.read()


entities_list = ent.replace("[","").replace("]","").replace("'","").strip().split(",")

formatted_entites_list = list()
for el in entities_list:
    formatted_entites_list.append(el.strip())

entities_dict= dict()

for entity in formatted_entites_list:
    cat = entity.split(":")[1]
    name = entity.split(":")[0]
    if cat not in entities_dict.keys():
        entities_dict[cat] = [name]
    else:
        entities_dict[cat].append(name)




with open("data/narrQA_questions_formatted.txt") as f:
    questions = set(f.readlines())

print(entities_dict)
out_list = list()
for quest in questions: #for each question format
    #print(quest)
    
    permu_list = [quest]
    for perms in permu_list:
        #print(perms)
        for word in perms.split(): #examine each word in the question
            word_f = word.strip("$").lower()
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
with open("data/questions_out2.txt","w") as f:
    f.writelines(out_list)
#out_question_list = list()
#for qs in quests:
#    print(qs)
    
"""
with open("data/question_out.txt","w+") as f:
    f.writelines(out_question_list)


out_ent_list = list()
for ent in formatted_entites_list:
        print(ent)
        out_string = ent.split(":")[0] + "\n"
        print(out_string)
        out_ent_list.append(out_string)
with open("data/entities_out.txt","w+") as f:
    f.writelines(out_ent_list)
"""
