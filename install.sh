pip install wikipedia vosk pyaudio pydub spacy gtts
python -m spacy download en_core_web_sm #Download spaCy model
MIMIR_DIR=$(pwd)"/"
echo $MIMIR_DIR
export MIMIR_DIR
mkdir speech_recognition/live_models
unzip speech_recognition/live_models/tdnn_1d_sp_chain_online.zip -d speech_recognition/live_models/
