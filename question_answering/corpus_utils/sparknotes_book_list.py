from utils import csv_to_list, levenshtein
import os
import os.path as op
import re
import requests
import sys
spark_lit_page = requests.get("https://www.sparknotes.com/lit/")

lit_page_text = spark_lit_page.text

title_regex = re.compile(r'__card__title__link--full-card-link"\s*href="\S*">(.*)</')

spark_books = re.findall(title_regex, lit_page_text)

if len(sys.argv) == 1:
	NarrativeQADir = os.environ["NARRATIVEQA_DIR"] #Set this environment variable for convenience
else:
	NarrativeQADir = sys.argv[1]

docs_file_path = op.join(NarrativeQADir, "documents.csv")

docs_list = csv_to_list(docs_file_path)
nqa_books = []

for line in docs_list:
	try:
		if line[2] == "gutenberg":
			nqa_books.append(line[-4])
	except:
		pass

for i in range(len(nqa_books)):
	if nqa_books[i].endswith(" (novel)"):
		nqa_books[i] = nqa_books[i][:-8]

both_books = set(nqa_books).intersection(set(spark_books))


print("N. books in NarrativeQA: {}".format(len(nqa_books)))
print("N. books on SparkNotes: {}".format(len(spark_books)))
print("N. books in both: {}".format(len(both_books)))
print("List of titles:")
print(both_books)


def check_for_missed_titles():
	for book in nqa_books:
		if book not in both_books:
			print("{} - {}".format(book, min(spark_books, key = lambda x: levenshtein(x, book))))
			input("Press enter to check next")
