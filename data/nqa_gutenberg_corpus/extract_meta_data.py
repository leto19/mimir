import os
import csv


data = [] 
extract_dir = "./train"
for root, dirs, files in os.walk(extract_dir, topdown=False):
  for name in files:
    with open(extract_dir+'/'+name) as f:
      for line in f:
        line = line.rstrip()
        if 'Author:' in line:
          author = line[line.index('Author: ') + len('Author: '):]
          data.append([name, author])
          break

with open("supported_books.csv", 'w', newline='') as csvfile:
  writer = csv.writer(csvfile)
  writer.writerow(['Title', 'Author'])
  writer.writerows(data)