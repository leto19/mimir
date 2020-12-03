import requests
import sys

"""
Takes a text file containing a corpus as argument and returns the ziped tarball containing the .lm and .dic,
using http://www.speech.cs.cmu.edu/tools/lmtool-new.html 
"""


corp_file = sys.argv[1]
f = open(corp_file,'rb')
print(f)
url = "http://www.speech.cs.cmu.edu/cgi-bin/tools/lmtool/run"
files = {'formtype': 'simple','corpus': f}

r = requests.post(url,files=files)
for lines in r.text.split("\n"):  # find download link
    print(lines)
    if '<a href="http://www.speech.cs.cmu.edu/tools/product/' in lines:
        dl_link = lines
#print(dl_link)
dl_link = dl_link.replace("<a href=","")
dl_link = dl_link.replace("</a> is the compressed version.","")
dl_link = dl_link.split(">")[0].strip()
dl_link = dl_link[1:-1]
print("dl_link:",dl_link)
dict_responce = requests.get(
        dl_link, allow_redirects=True)
out_file_name = sys.argv[1].replace(".txt","_model.tgz")
open(out_file_name, 'wb').write(
    dict_responce.content)
