from utils import csv_to_list, make_id_name_dict
import os 
import os.path as op

mimir_dir = os.environ["MIMIR_DIR"] #Set to Mimir root directory
nqa_dir = os.environ["NARRATIVEQA_DIR"] #Set to NarrativeQA root directory

summary_dir = op.join(mimir_dir, "data", "nqa_summary_text_files")
summary_csv = op.join(nqa_dir, "third_party", "wikipedia", "summaries.csv")

id_name_dict = make_id_name_dict()

if __name__ == "__main__":
	summary_list = csv_to_list(summary_csv)
	
	for row in summary_list[1:]:
		print(row)
		doc_id, corpus_set, summary, _ = row
		if doc_id in id_name_dict: #We are excluding the movies
			book_name = id_name_dict[doc_id]
			with open(op.join(summary_dir, corpus_set, book_name), "w+") as txtfile:
				txtfile.write(summary)
