import sounddevice as sd
from scipy.io.wavfile import write
import time
from threading import Thread
import os
import tkinter
from tkinter import ttk
import json

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


class Enregistreur(Thread):
    def __init__(self, Stream, duree, nom):
        Thread.__init__(self)
        self.duree = duree
        self.perma_save = False
        self.follow = True
        self.nom = nom
        self.Stream = Stream
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
                            self.nom + "_%Y_%m_%d_%H_%M_%S_part2",
                            time.gmtime(time.time()),
                        )
                    )
                    + ".wav"
                )
                write(self.nom + "\\" + name, fs, record)
                self.perma_save = False

            else:
                write("tmp_" + self.nom + ".wav", fs, record)


def start_record():

    duree_enregistrement = 1  # En minutes
    config = load_setings()

    d = sd.query_devices()

    channel_discord = -1
    channel_micro = -1

    list_to_record = []
    stream_list = []
    listener_list = []

    for k in range(0, len(d)):
        for entry in config["entries"]:
            if (
                d[k]["name"] == entry["name"]
                and d[k]["hostapi"] == 0
                and d[k]["max_input_channels"] > 0
            ):
                list_to_record.append([k, entry["label"]])

    for record in list_to_record:
        verify_dir(record[1])
    for record_param in list_to_record:
        if record_param[0] != -1:
            stream_list.append(
                [
                    sd.InputStream(
                        samplerate=44100,
                        device=record_param[0],
                        dtype="float32",
                    ),
                    record_param[1],
                ]
            )

    for stream in stream_list:
        stream[0].start()
        listener_list.append(
            [
                Enregistreur(stream[0], 60 * duree_enregistrement, stream[1]),
                stream[1],
            ]
        )

    for listener in listener_list:
        listener[0].start()

    while True:
        if (
            str(
                input(
                    "Ecrivez quelque chose si vous voulez enregistrer les "
                    + str(2 * duree_enregistrement)
                    + " dernieres minutes : "
                )
            )
            == "stop"
        ):
            for listener in listener_list:
                listener[0].stop()
            for listener in listener_list:
                listener[0].join()
            exit()
        for listener in listener_list:
            listener[0].perma_save = True

            filename = (
                str(
                    time.strftime(
                        f"{listener[1]}_%Y_%m_%d_%H_%M_%S_part1",
                        time.gmtime(time.time()),
                    )
                )
                + ".wav"
            )
            tmp = f"tmp_{listener[1]}.wav"
            if os.path.exists(tmp):
                os.rename(tmp, listener[1] + "\\" + filename)

        print(
            "Les dernieres minutes sont en cours de traitement, deux fichiers seront bientot cree."
        )
        print(
            "-------------------------------------------------------------------"
        )


def load_setings():
    with open("config.txt", "r") as f:
        try:
            config = json.loads(f.read())
        except:
            return {"entries": []}
        return config


start_record()
