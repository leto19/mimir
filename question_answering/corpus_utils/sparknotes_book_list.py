import csv 
import os
import os.path as op
import re
import requests

spark_lit_page = requests.get("https://www.sparknotes.com/lit/")

lit_page_text = spark_lit_page.text

title_regex = re.compile(r'__card__title__link--full-card-link"\s*href="\S*">(.*)</')

spark_books = re.findall(title_regex, lit_page_text)

NarrativeQADir = "/home/jonathan/Desktop/corpora/narrativeqa-master"
docs_file_path = op.join(NarrativeQADir, "documents.csv")

def csv_to_list(csv_file_path):
	line_list = []
	
	with open(csv_file_path, newline="") as csvfile:
		csvreader = csv.reader(csvfile)
		for row in csvreader:
			line_list.append(row)

	return(line_list)


docs_list = csv_to_list(docs_file_path)
nqa_books = []

for line in docs_list:
	try:
		if line[2] == "gutenberg":
			nqa_books.append(line[-4])
	except:
		pass


both_books = set(nqa_books).intersection(set(spark_books))

print("N. books in NarrativeQA: {}".format(len(nqa_books)))
print("N. books on SparkNotes: {}".format(len(spark_books)))
print("N. books in both: {}".format(len(both_books)))
print("List of titles:")
print(both_books)
