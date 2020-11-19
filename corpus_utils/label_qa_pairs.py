import csv
import numpy as np
import os
import os.path as op
import pandas as pd
#import pandastable    # Use these for ease of viewing labels so far
#import tkinter as tk
import re
from utils import csv_to_list, load_or_create_object
import sys

if len(sys.argv) == 1:
	MimirDir = os.environ["MIMIR_DIR"] #Set to Mimir root directory
	NarrativeQADir = os.environ["NARRATIVEQA_DIR"] #Set to NarrativeQA root directory
elif len(sys.argv) == 3:
	MimirDir = sys.argv[1]
	NarrativeQADir = sys.argv[2]


qaps_line_list = csv_to_list(op.join(NarrativeQADir, "qaps.csv"))
header = qaps_line_list[0]
header.append("answer type")
answer_lines = qaps_line_list[1:]
labels_list_name = op.join(MimirDir, "data","labels_list_tmp.npy")
labels_list = load_or_create_object(labels_list_name, [None] * len(answer_lines))

continue_index = 0

for i in range(len(labels_list)):
	if labels_list[i] == None:
		break
	continue_index += 1
		
labels_dict = {1: "PER", 2: "ORG", 3: "LOC", 4: "DES", 5: "OTH"}

start_input = input("Answer category labeller.\n\
[s] Start labelling from next unlabelled question.\n\
[v] View labels so far \n\
[0,1,2...] Start labelling from an index\n\
[q] Quit \n")

if start_input == "s":
	i = continue_index
elif re.match(r"[0-9]+", start_input):
	i = start_input
elif start_input == "v":
	import pandastable
	import tkinter as tk
	root = tk.Tk()
	root.maxsize()
	frame = tk.Frame(root)
	frame.pack(fill="both", expand="true")
	for i in range(len(answer_lines)):
		answer_lines[i].append(labels_list[i])
	table = [header] + answer_lines
	df = pd.DataFrame(table)
	table = pandastable.Table(parent=frame, dataframe=df)
	table.show()
	root.mainloop()

os.system("clear")
my_input = ""

while (my_input != "q") and (i < len(answer_lines)-1):
	line = answer_lines[i]
	print("Question {0} of {1}:".format(i + 1, len(answer_lines)))
	print(line[2])
	print("Answers:")
	print(line[3],line[4])
	my_input = input("Select answer type:\n\
[1]: person [2] organization [3] location [4] personal description [5] other \n\
[b] back [n] next [q] quit ")
	if my_input in "12345":
		labels_list[i] =  labels_dict[int(my_input)]
		np.save(labels_list_name, np.array([labels_list]))
		i += 1
	elif my_input == "n":
		i += 1
	elif my_input == "b":
		i -= 1
	elif my_input == "q":
		exit(1)
	os.system("clear")
