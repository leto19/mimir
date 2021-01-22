import os
import sys
import zipfile
from get_speech_input import get_audio
from shutil import rmtree
from time import sleep
import getpass
def record_test_set():
    try:
        # Create target Directory
        os.mkdir("auto_speech_recognition/audio_temp")
    except FileExistsError:
        print("Directory already exists")
    with open(sys.argv[1]) as f:
        baseline_list = f.readlines()
    baseline_index = 0
    os.system('clear')
    for q in baseline_list:
        print("Please say '%s'\n(Press Enter to continue)"%q.replace("\n",""))
        input()
        out_name = "auto_speech_recognition/audio_temp/q%s.wav" % baseline_index
        get_audio(seconds= 10,out_file=out_name)
        baseline_index+=1
        os.system('clear')
  
def zip_test_set(folder="auto_speech_recognition/audio_temp"):
    zipf = zipfile.ZipFile('test_set_%s.zip'% getpass.getuser(),'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(folder):
        for file in files:
            zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(folder, '..')))


record_test_set()
zip_test_set()
rmtree("auto_speech_recognition/audio_temp")
print("Thank you!")
sleep(1)