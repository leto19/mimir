pip install wikipedia vosk pyaudio pydub spacy gtts scipy wave torch pysndfx
transformers sentence_transformers soundfile noisereduce
python -m spacy download en_core_web_sm #Download spaCy model


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
mv models/T5_base_finetuned/epoch1 models/T5
rm -rf models/T5_base_finetuned
rm models/${filename}

export PATH="$PATH:."

rm cookie 