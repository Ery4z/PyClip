import sounddevice as sd
from scipy.io.wavfile import write
import time
from threading import Thread
import os
import tkinter
from tkinter import ttk
import json
from pydub import AudioSegment
from pynput import keyboard
from datetime import datetime
WANTED_KEY = keyboard.Key.f2




FILE_PATH = os.path.dirname(os.path.realpath(__file__))

os.system("cls")
p = os.path.realpath(__file__)
path = os.path.dirname(p)
tmp1 = os.path.join("tmp_Discord.wav")
tmp5 = os.path.join("tmp_Micro.wav")

if os.path.exists(tmp1):
    os.remove(tmp1)

if os.path.exists(tmp5):
    os.remove(tmp5)


def verify_dir(dir):
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), dir)
    isExist = os.path.exists(path)

    if not isExist:

        # Create a new directory because it does not exist
        os.makedirs(path)

class ConvertFile(Thread):
    def __init__(self, filepath,from_type="wav",to_type="mp3"):
        Thread.__init__(self)
        self.filepath = filepath
        self.from_type = from_type
        self.to_type = to_type
        
    def run(self):
        new_filepath= self.filepath.replace("."+self.from_type,"."+self.to_type)
        sound = AudioSegment.from_wav(self.filepath)
        sound.export(new_filepath, format=self.to_type)
        os.remove(self.filepath)



class Enregistreur(Thread):
    def __init__(self, Stream, duree, nom, pipe):
        Thread.__init__(self)
        self.duree = duree
        self.perma_save = False
        self.follow = True
        self.nom = nom
        self.Stream = Stream
        self.pipe = pipe
        print("Thread " + self.nom + " initialise.")

    def Save(self):
        self._perma_save = True

    def Stop(self):
        self.follow = False

    def run(self):
        while self.follow:
            # print(self.nom + " nouveau stack")
            fs = 44100
            # t1 = time.time()
            record = self.Stream.read(int(self.duree * fs))

            record = record[0]
            if self.perma_save:
                name = (
                    str(
                        time.strftime(
                            self.nom + "_%Y_%m_%d__%H_%M_%S_part2",
                            time.gmtime(time.time()),
                        )
                    )
                    + ".wav"
                )
                
                filename_2 = os.path.join(FILE_PATH,"record_"+self.nom + "\\" + name)
                filename_1 = self.pipe.get_to_process()
                
                filename_final = filename_1.replace("_part1","")
                
                write(filename_2, fs, record)
                time.sleep(2)
                file_converter = ConvertFile(filename_2)
                file_converter.start()
                file_converter.join()
                try:
                    file_1 = AudioSegment.from_mp3(filename_1)
                except :
                    file_1 = AudioSegment.empty()
                
                try:
                    file_2 = AudioSegment.from_mp3(filename_2.replace("wav","mp3"))
                except :
                    file_2 = AudioSegment.empty() 
                file_final = file_1 + file_2
                file_final.export(filename_final, format="mp3")
                os.remove(filename_1)
                os.remove(filename_2.replace("wav","mp3"))
                self.pipe.flush_to_process()
                
                print(f"{datetime.now().strftime('%H:%M:%S')} | Processing {self.nom} finished.                                                    ")
                print("Waiting for the F2 key to be pressed to start recording...                                                    ", end="\r")
                
                
                self.perma_save = False

            else:
                write(os.path.join(FILE_PATH,"tmp_" + self.nom + ".wav"), fs, record)
                self.pipe.global_pipe.ready_status = True

class RecorderPipe:
    def __init__(self,global_pipe):
        self.to_process = None
        self.global_pipe = global_pipe
    def set_to_process(self, to_process):
        self.to_process = to_process
    def get_to_process(self):
        return self.to_process
    def flush_to_process(self):
        self.to_process = None

class GlobalPipe:
    ready_status = False

def start_record():

    duree_enregistrement = 1  # En minutes
    config = load_setings()

    d = sd.query_devices()

    channel_discord = -1
    channel_micro = -1

    list_to_record = []
    stream_list = []
    listener_list = []
    
    global_pipe = GlobalPipe()
    
    
    
    
    


    for k in range(0, len(d)):
        for entry in config["entries"]:
            if (
                d[k]["name"] == entry["name"]
                and d[k]["hostapi"] == 0
                and d[k]["max_input_channels"] > 0
            ):
                list_to_record.append([k, entry["label"]])

    for record in list_to_record:
        verify_dir("record_"+record[1])
    for record_param in list_to_record:
        if record_param[0] != -1:
            stream_list.append(
                [
                    sd.InputStream(
                        samplerate=44100,
                        device=record_param[0],
                        dtype="float32",
                    ),
                    record_param[1]
                ]
            )

    for stream in stream_list:
        stream[0].start()
        pipe = RecorderPipe(global_pipe)
        
        listener_list.append(
            [
                Enregistreur(stream[0], 60 * duree_enregistrement, stream[1], pipe),
                stream[1],pipe
            ]
        )

    for listener in listener_list:
        listener[0].start()
        
    print(f"{datetime.now().strftime('%H:%M:%S')} | Recorders armed. Please wait for the recording process to setup...                           ", end="\r")
    while not global_pipe.ready_status:
        time.sleep(1)
    print(f"{datetime.now().strftime('%H:%M:%S')} | Recorders ready. Please press F2 to capture last two minutes.                           \a", end="\r")

    def on_release(key):
        
        if key == WANTED_KEY:
                # Stop listener
                print(f"{datetime.now().strftime('%H:%M:%S')} | Processing the last two minutes please wait...                                                    \a", end="\r")
                
                for listener in listener_list:
                    listener[0].perma_save = True

                    filename = (
                        str(
                            time.strftime(
                                f"{listener[1]}_%Y_%m_%d__%H_%M_%S_part1",
                                time.gmtime(time.time()),
                            )
                        )
                        + ".wav"
                    )
                    tmp = os.path.join(FILE_PATH,f"tmp_{listener[1]}.wav")
                    if os.path.exists(tmp):
                        file_path = os.path.join(FILE_PATH,"record_" + listener[1] + "\\" + filename)
                        os.rename(tmp, file_path)
                        
                        listener[2].set_to_process(file_path.replace(".wav",".mp3"))
                        
                        file_converter = ConvertFile(file_path)
                        file_converter.start()
                
            
        

    # Collect events until released
    with keyboard.Listener(
            on_release=on_release) as listener:
        listener.join()




def load_setings():
    with open(os.path.join(FILE_PATH,"config.json"), "r") as f:
        try:
            config = json.loads(f.read())
        except:
            return {"entries": []}
        return config


start_record()
