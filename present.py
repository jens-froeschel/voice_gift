#!/usr/bin/env python3

import argparse
import os
import queue
import sounddevice as sd
import vosk
import sys
import json
import pygame
import pygame._sdl2 as sdl2

#For wake button call
import RPi.GPIO as GPIO
BUTTON = 17


q = queue.Queue()
name_file = open("names.txt", "r")
name_list = name_file.read().splitlines()
name_list = list(filter(len, name_list))
name_map = {}
with open("names_map.txt") as f:
    for line in f:
        if len(line)<2:
            continue
        (key, val) = line.split("|")
        name_map[key] = val.strip()

inverse_name_map = {v: k for k, v in name_map.items()}
audiodevice="USB Device 0x1908:0x332a, USB Audio"

print("--------------")
print( str(name_list) )
print("--------------")
print(str(name_map))
print("--------------")


pygame.init()
is_capture = 0  # zero to request playback devices, non-zero to request recording devices
num = sdl2.get_num_audio_devices(is_capture)
names = [str(sdl2.get_audio_device_name(i, is_capture), encoding="utf-8") for i in range(num)]
print("")
print("Listing available Audio Devices (set in present.py as audiodevice:")
print("\n".join(names))
print("")
pygame.quit()



recording = False
def button_callback(channel):
    global recording
    recording = True
    print("Button Pressed!")

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin to be an input pin and set initial value to be pulled low (off)

GPIO.add_event_detect(BUTTON,GPIO.RISING,callback=button_callback) # Setup event on pin rising edge


def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status)
    q.put(bytes(indata))

def replace_words_list(name_list, name_map):
    return list(map(name_map.get, name_list))
    
def replace_words_string(s, words):
    for k, v in words.items():
        s = s.replace(k, v)
    return s

def play_audio(name):
    name = name.lower().replace(" ","_")
    f="audiofiles/"+str(name)+".wav"
    if( not os.path.isfile(f)):
        print("File "+str(f)+" doesn't exist")
        return
    print("Playing "+str(f))
    global recording
    recording = False
    pygame.mixer.pre_init(devicename=audiodevice)
    pygame.mixer.init()
    pygame.mixer.music.load(f)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        continue


mapped_name_list = replace_words_list(name_list, name_map)

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
    '-l', '--list-devices', action='store_true',
    help='show list of audio devices and exit')
args, remaining = parser.parse_known_args()
if args.list_devices:
    print(sd.query_devices())
    parser.exit(0)
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[parser])
parser.add_argument(
    '-f', '--filename', type=str, metavar='FILENAME',
    help='audio file to store recording to')
parser.add_argument(
    '-m', '--model', type=str, metavar='MODEL_PATH',
    help='Path to the model')
parser.add_argument(
    '-d', '--device', type=int_or_str,
    help='input device (numeric ID or substring)')
parser.add_argument(
    '-r', '--samplerate', type=int, help='sampling rate')
args = parser.parse_args(remaining)

try:
    if args.model is None:
        args.model = "model"
    if not os.path.exists(args.model):
        print ("Please download a model for your language from https://alphacephei.com/vosk/models")
        print ("and unpack as 'model' in the current folder.")
        parser.exit(0)
    if args.samplerate is None:
        device_info = sd.query_devices(args.device, 'input')
        # soundfile expects an int, sounddevice provides a float:
        args.samplerate = int(device_info['default_samplerate'])

    model = vosk.Model(args.model)

    if args.filename:
        dump_fn = open(args.filename, "wb")
    else:
        dump_fn = None

    with sd.RawInputStream(samplerate=args.samplerate, blocksize = 8000, device=args.device, dtype='int16',
                            channels=1, callback=callback):
            print('#' * 80)
            print('Press Ctrl+C to stop the recording')
            print('#' * 80)

            #rec = vosk.KaldiRecognizer(model, args.samplerate)
            rec = vosk.KaldiRecognizer(model, args.samplerate, str(mapped_name_list).replace("'","\""))
            while True:
                data = q.get()
                if(not recording):
                    #print("Not recording ("+str(recording)+"), continue!")
                    continue
                if rec.AcceptWaveform(data):
                    res = rec.Result()
                    res_text = json.loads(res)['text']
                    mapped_name = replace_words_string(res_text, inverse_name_map)
                    print(res)
                    play_audio(mapped_name)
                    with q.mutex:
                        q.queue.clear()
                else:
                    pass
                    print(rec.PartialResult())
                if dump_fn is not None:
                    dump_fn.write(data)

except KeyboardInterrupt:
    print('\nDone')
    parser.exit(0)
except Exception as e:
    parser.exit(type(e).__name__ + ': ' + str(e))

