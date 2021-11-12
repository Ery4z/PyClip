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
                write(name, fs, record)
                self.perma_save = False

            else:
                write("tmp_" + self.nom + ".wav", fs, record)


def start_record(
    output1="CABLE-A Output (VB-Audio Cable ",
    output2="CABLE Output (VB-Audio Virtual ",
):

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
                d[k]["name"] == output1
                and d[k]["hostapi"] == 0
                and d[k]["max_input_channels"] > 0
            ):
                list_to_record.append([k, entry["label"]])

    print(list_to_record)
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
        stream.start()
        listener_list.append(
            [
                Enregistreur(stream[0], 60 * duree_enregistrement, stream[1]),
                stream[1],
            ]
        )

    for listener in listener_list:
        listener.start()

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
                os.rename(tmp, filename)

        print(
            "Les dernieres minutes sont en cours de traitement, deux fichiers seront bientot cree."
        )
        print(
            "-------------------------------------------------------------------"
        )


def valid_start(in1, in2, window=None):
    if window is not None:
        window.destroy()
    start_record(output1=in1, output2=in2)


def load_setings():
    with open("config.txt", "r") as f:
        config = json.load(f.read())
        return config


def save_settings(periph_select, label_select, window=None):
    config = {
        "entries": [
            {"name": periph_select[0].get(), "label": label_select[0].get()},
            {"name": periph_select[1].get(), "label": label_select[1].get()},
        ]
    }
    if window is not None:
        window.destroy()
    with open("config.txt", "w") as f:
        f.write(json.dumps(config))


def choose():
    list_devices = sd.query_devices()
    real_list = []
    for device in list_devices:
        if device["hostapi"] == 0 and device["max_input_channels"] > 0:
            real_list.append(device)

    name_list = [device["name"] for device in real_list]
    window = tkinter.Tk()

    window.title("Welcome to LikeGeeks app")

    window.geometry("350x200")
    label1 = tkinter.Label(window, text="In1")
    label1.grid(column=0, columnspan=1, row=1)
    label2 = tkinter.Label(window, text="In2")
    label2.grid(column=0, columnspan=1, row=2)

    labelPeriph = tkinter.Label(window, text="Periph")
    labelPeriph.grid(column=1, columnspan=4, row=0)
    labelLabel = tkinter.Label(window, text="Label")
    labelLabel.grid(column=5, columnspan=4, row=0)

    entry1 = tkinter.Entry(window)
    entry1.grid(column=5, columnspan=4, row=1)

    combo_1 = ttk.Combobox(window)
    combo_1["values"] = name_list
    combo_1.current(1)  # set the selected item
    combo_1.grid(column=1, columnspan=4, row=1)

    entry2 = tkinter.Entry(window)
    entry2.grid(column=5, columnspan=4, row=2)

    combo_2 = ttk.Combobox(window)
    combo_2["values"] = name_list
    combo_2.current(1)  # set the selected item
    combo_2.grid(column=1, columnspan=4, row=2)
    periph_select = [combo_1, combo_2]
    label_select = [entry1, entry2]
    b_valid = tkinter.Button(
        window,
        text="Valid",
        command=lambda: save_settings(
            periph_select, label_select, window=window
        ),
    )
    b_valid.grid(column=0, columnspan=4, row=3)

    window.mainloop()


choose()
