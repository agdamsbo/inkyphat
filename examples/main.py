#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import signal
import buttonshim
import os
from PIL import Image, ImageFont, ImageDraw
from inky import InkyPHAT
import time
import urllib2
import textwrap


def flash_led(interval, times, r, g, b):
    for i in range(times):
        buttonshim.set_pixel(r, g, b)
        time.sleep(interval)
        buttonshim.set_pixel(0, 0, 0)
        time.sleep(interval)

def buttonflash():
    flash_led(0.025, 3, 255, 255, 255) 

def runprocess(file):
    try:
        # run process
        process = subprocess.Popen(file, shell=True)
        # flash green led to show its working
        flash_led(0.5, 14, 0, 255, 0)
        # wait for the process to complete
        process.communicate()
        # flash blue led to show its finshed
        flash_led(0.05, 5, 0, 0, 255)   
    except Exception as error:
        printtoscreen("Error", error)


def wait_for_internet_connection():
    while True:
        try:
            response = urllib2.urlopen('http://www.google.com',timeout=1)
            runprocess('/home/pi/scripts/phat/weather-home.py  --type "phat" --colour "red"')
            return
        except urllib2.URLError:
            pass
            printtoscreen("Message","Waitng for internet connection")


# Button presses/release

# Button A - Runs a QR code example
@buttonshim.on_release(buttonshim.BUTTON_A)
def button_a(button, pressed):
    buttonflash()
    runprocess("/home/pi/Pimoroni/inkyphat/examples/qr.py red 'http://www.electromaker.io'")

# Button B - runs home weather script after weather example
@buttonshim.on_release(buttonshim.BUTTON_B)
def button_b(button, pressed):
    buttonflash()
    runprocess('/home/pi/scripts/phat/weather-home.py --type "phat" --colour "red"')


# Button C - runs the weather - IP - time/date and system info splash screen - updates every 10 minutes
@buttonshim.on_release(buttonshim.BUTTON_C)
def button_c(button, pressed):
    buttonflash()
    # Refresh it every 600 seconds to stop loop must restart service process - hold button A
    starttime=time.time()
    while True:
        runprocess("/home/pi/scripts/phat/info.py")
        time.sleep(600.0 - ((time.time() - starttime) % 600.0))

# Button D - Runs a image display example
@buttonshim.on_release(buttonshim.BUTTON_D)
def button_d(button, pressed):
    buttonflash()
    runprocess('/home/pi/scripts/phat/sign.py --type "phat" --colour "red" --name "Andreas"')

# Button E - Runs the name badge example
@buttonshim.on_release(buttonshim.BUTTON_E)
def button_e(button, pressed):
    buttonflash()
    runprocess('/home/pi/scripts/phat/sign.py --type "phat" --colour "red" --name "Anne"')


# BUTTTON HOLDS

# Restarts Service    
@buttonshim.on_hold(buttonshim.BUTTON_A)
def button_a_hold(button):
    flash_led(0.05, 3, 255, 0, 0)
    os.system('sudo svc -k /etc/service/phat/')

# Reboots Pi
@buttonshim.on_hold(buttonshim.BUTTON_B)
def button_b_hold(button):
    flash_led(0.05, 3, 255, 0, 0)
    os.system('sudo reboot')

# Shutdown Pi
@buttonshim.on_hold(buttonshim.BUTTON_C)
def button_c_hold(button):
    flash_led(0.05, 3, 255, 0, 0)
    os.system('sudo shutdown -h now')


# Run initial python script info.py when internet connection established
wait_for_internet_connection()

signal.pause()
