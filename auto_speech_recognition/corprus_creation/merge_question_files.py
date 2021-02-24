import os
root = "data/question_files/"
with open ("data/question_files/1all_qs.txt","a") as f:
    for path, subdirs, files in os.walk(root):
        for fil in files:
            f.writelines(open(os.path.join(root,fil),"r").readlines())

