import os
import tkinter
from tkinter import ttk
import json
import sounddevice as sd


def Settings():
    
    
    
    try:
        config = load_setings()
    except FileNotFoundError:
        config = {"entries":[],"startup": 0}
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.json"), "w") as f:
            f.write(json.dumps(config))
            
    devices_selected = []
    for entry in config["entries"]:
        devices_selected.append([entry["name"], entry["label"]])
    list_devices = sd.query_devices()
    real_list = []
    for device in list_devices:
        if device["hostapi"] == 0 and device["max_input_channels"] > 0:
            real_list.append(device)

    name_list = [device["name"] for device in real_list]
    window = tkinter.Tk()

    window.title("PyClip Settings")

    # window.geometry("500x")
    label1 = tkinter.Label(window, text="In")
    label1.grid(column=0, columnspan=1, row=1)

    labelPeriph = tkinter.Label(window, text="Periph")
    labelPeriph.grid(column=1, columnspan=5, row=0)
    labelLabel = tkinter.Label(window, text="Label")
    labelLabel.grid(column=6, columnspan=5, row=0)

    entry1 = tkinter.Entry(window)
    entry1.grid(column=6, columnspan=5, row=1)

    combo_1 = ttk.Combobox(window)
    combo_1["values"] = name_list
    combo_1.current(1)  # set the selected item
    combo_1.grid(column=1, columnspan=5, row=1)

    b_add = tkinter.Button(
        window,
        text="Add",
        command=lambda: add_entry(
            combo_1.get(),
            entry1.get(),
            list_box_devices,
            config,
        ),
    )
    b_add.grid(column=11, columnspan=1, row=1)

    list_box_devices = tkinter.Listbox(window, width=50, height=5)
    list_box_devices.grid(column=1, columnspan=10, row=3)
    for devices in devices_selected:
        list_box_devices.insert("end", f"{devices[0]} | {devices[1]}")

    b_remove = tkinter.Button(
        window,
        text="Remove entry",
        command=lambda: remove_entry(
            list_box_devices.get(list_box_devices.curselection()),
            list_box_devices,
            config,
        ),
    )
    b_remove.grid(column=1, columnspan=1, row=4)

    if "startup" in config:
        default_check = config["startup"]
    else:
        default_check = 0

    check = tkinter.IntVar(value=default_check)
    startupbutton = tkinter.Checkbutton(
        window,
        text="Start on startup",
        variable=check,
        onvalue=1,
        offvalue=0,
        command=lambda: startup(check, config),
    )
    startupbutton.grid(column=12, columnspan=1, row=3)

    b_valid = tkinter.Button(
        window,
        text="Save Settings",
        command=lambda: save_settings(config, window=window),
    )
    b_valid.grid(column=1, columnspan=1, row=5)

    window.mainloop()


def add_entry(entry, label, list_box_devices, config):

    list_box_devices.insert("end", f"{entry} | {label}")
    config["entries"].append({"name": entry, "label": label})


def remove_entry(entry, list_box_devices, config):

    selected_checkboxs = list_box_devices.curselection()

    for selected_checkbox in selected_checkboxs[::-1]:
        list_box_devices.delete(selected_checkbox)

    l = entry.split(" | ")
    device = l[0]
    label = l[1]
    for entry in config["entries"]:
        if entry["name"] == device:
            config["entries"].remove(entry)
    return 0


def startup(value, config):
    config["startup"] = value.get()


def load_setings():
    config_file = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "config.json"
    )
    with open(config_file, "r") as f:
        try:
            config = json.loads(f.read())
        except:
            return {"entries": []}
        return config


def save_settings(config, window=None):
    config_file = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "config.json"
    )
    start_app_address = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "run.py"
    )
    startup_file = f"{os.path.dirname(os.path.realpath(__file__))}\\StartupPyClip.cmd"

    if config["startup"]:
        with open(startup_file, "w") as f:
            f.write(
                f"cd {os.path.dirname(os.path.realpath(__file__))}\npython run.py")

    if window is not None:
        window.destroy()
    with open(config_file, "w") as f:
        f.write(json.dumps(config))


Settings()
