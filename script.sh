fileid="1vipUEx7Yyokz14PSHik_r6hK04FPYkNc"
filename="distilbert.zip"
echo "downloading ${filename}"
curl -c ./cookie -s -L "https://drive.google.com/uc?export=download&id=${fileid}" > /dev/null
curl -Lb ./cookie "https://drive.google.com/uc?export=download&confirm=`awk '/download/ {print $NF}' ./cookie`&id=${fileid}" -o models/${filename}
unzip models/${filename} -d models
mv models/epoch2 models/distilbert
rm models/${filename}

