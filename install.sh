pip install wikipedia vosk pyaudio pydub spacy gtts scipy noisereduce wave 
python -m spacy download en_core_web_sm #Download spaCy model


mkdir dialogue/models/fastText
curl -Lo dialogue/models/fastText/crawl-300d-2M.vec.zip https://dl.fbaipublicfiles.com/fasttext/vectors-english/crawl-300d-2M.vec.zip
unzip -o dialogue/models/fastText/crawl-300d-2M.vec.zip -d dialogue/models/fastText/

mkdir dialogue/models/encoder
curl -Lo dialogue/models/encoder/infersent2.pkl https://dl.fbaipublicfiles.com/infersent/infersent2.pkl


fileid="1mPZDW1jpTYcX5dE16H3EzHBGHPuOY9v6"
filename="all.zip"
echo "downloading ${filename}"
curl -c ./cookie -s -L "https://drive.google.com/uc?export=download&id=${fileid}" > /dev/null
curl -Lb ./cookie "https://drive.google.com/uc?export=download&confirm=`awk '/download/ {print $NF}' ./cookie`&id=${fileid}" -o models/${filename}
unzip models/${filename} -d models
rm models/${filename}


fileid="1vipUEx7Yyokz14PSHik_r6hK04FPYkNc"
filename="distilbert.zip"
echo "downloading ${filename}"
curl -c ./cookie -s -L "https://drive.google.com/uc?export=download&id=${fileid}" > /dev/null
curl -Lb ./cookie "https://drive.google.com/uc?export=download&confirm=`awk '/download/ {print $NF}' ./cookie`&id=${fileid}" -o models/${filename}
unzip models/${filename} -d models
mv models/epoch2 models/distilbert
rm models/${filename}

fileid="1vwix56je4AT6GkXNU0sK51bJzfUiAByy"
filename="t5_base_finetuned.zip"
echo "downloading ${filename}"
curl -c ./cookie -s -L "https://drive.google.com/uc?export=download&id=${fileid}" > /dev/null
curl -Lb ./cookie "https://drive.google.com/uc?export=download&confirm=`awk '/download/ {print $NF}' ./cookie`&id=${fileid}" -o models/${filename}
unzip models/${filename} -d models
mv models/T5_base_finetuned/epoch1 models/t5
rm -rf models/T5_base_finetuned
rm models/${filename}


fileid="1hU3oFe8Q9BQfkDirj0MMRjtr9RCfaMeR"
filename="qc_rnn_model.zip"
echo "downloading ${filename}"
curl -c ./cookie -s -L "https://drive.google.com/uc?export=download&id=${fileid}" > /dev/null
curl -Lb ./cookie "https://drive.google.com/uc?export=download&confirm=`awk '/download/ {print $NF}' ./cookie`&id=${fileid}" -o models/${filename}
unzip models/${filename} -d models
rm models/${filename}

rm cookie 