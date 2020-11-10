with open("data/entities.txt","r") as f:
    ent = f.read()


entities_list = ent.replace("[","").replace("]","").replace("'","").strip().split(",")

formatted_entites_list = list()
for el in entities_list:
    formatted_entites_list.append(el.strip())

formatted_entites_list = sorted(list(set(formatted_entites_list)))
formatted_entites_list.remove("")
print(formatted_entites_list)

with open("data/question_format.txt") as f:
    quests = f.readlines()

out_question_list = list()
for qs in quests:
    for ents in formatted_entites_list:
        print(qs % ents)
        out_question_list.append(qs % ents)

with open("data/question_out.txt","w+") as f:
    f.writelines(out_question_list)