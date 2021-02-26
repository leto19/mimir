pip install wikipedia vosk pyaudio pydub spacy gtts scipy noisereduce wave aubio
#python -m spacy download en_core_web_sm #Download spaCy model
MIMIR_DIR=$(pwd)"/"
echo $MIMIR_DIR
export MIMIR_DIR

mkdir dialogue/models/fastText
curl -Lo dialogue/models/fastText/crawl-300d-2M.vec.zip https://dl.fbaipublicfiles.com/fasttext/vectors-english/crawl-300d-2M.vec.zip
unzip dialogue/models/fastText/crawl-300d-2M.vec.zip -d dialogue/models/fastText/

mkdir dialogue/models/encoder
curl -Lo dialogue/models/encoder/infersent2.pkl https://dl.fbaipublicfiles.com/infersent/infersent2.pkl