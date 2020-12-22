from utils import csv_to_list, make_id_name_dict, make_name_url_dict
import os 
import os.path as op
import requests

mimir_dir = os.environ["MIMIR_DIR"] #Set to Mimir root directory
#nqa_dir = os.environ["NARRATIVEQA_DIR"] #Set to NarrativeQA root directory

data_dir = op.join(mimir_dir, "data")

full_text_dir = op.join(data_dir, "nqa_gutenberg_corpus")

if not op.exists(full_text_dir):
	os.mkdir(full_text_dir)

for d in ["test", "train", "valid"]:
	if not op.exists(op.join(full_text_dir, d)):
		os.mkdir(op.join(full_text_dir, d))

summary_csv = op.join(data_dir, "summaries.csv")

id_name_dict = make_id_name_dict()
name_url_dict = make_name_url_dict()

def make_dataset_dict():
	data_dir = op.join(mimir_dir, "data")
	summary_csv = op.join(data_dir, "summaries.csv")
	summary_list = csv_to_list(summary_csv)
	name_dataset_dict = {}
	for row in summary_list[1:]
		doc_id, corpus_set, _, _ = row
		book_name = id_name_dict[doc_id]
		name_dataset_dict[book_name] = corpus_set #Test, train, valid#
	return name_dataset_dict

if __name__ == "__main__":
	summary_list = csv_to_list(summary_csv)
	
	for row in summary_list[1:]:
		doc_id, corpus_set, summary, _ = row
		if doc_id in id_name_dict: #We are excluding the movies
			book_name = id_name_dict[doc_id]
			url= name_url_dict[book_name]
			print("getting {}".format(url))
			guten_page = requests.get(url)
			guten_text = guten_page.text	
			with open(op.join(full_text_dir, corpus_set, book_name), "w+") as txtfile:
				txtfile.write(guten_text)
