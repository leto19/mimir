pip install wikipedia vosk pyaudio pydub spacy gtts scipy noisereduce
python -m spacy download en_core_web_sm #Download spaCy model
MIMIR_DIR=$(pwd)"/"
echo $MIMIR_DIR
export MIMIR_DIR
mkdir auto_speech_recognition/live_models
unzip auto_speech_recognition/live_models/tdnn_1d_sp_chain_online.zip -d auto_speech_recognition/live_models/
