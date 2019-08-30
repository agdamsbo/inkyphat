#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import time
import urllib
import glob
import argparse
from PIL import Image, ImageFont, ImageDraw
from font_fredoka_one import FredokaOne
import subprocess
from inky import InkyPHAT

try:
    import requests
except ImportError:
    exit("This script requires the requests module\nInstall with: sudo pip install requests")

try:
    import geocoder
except ImportError:
    exit("This script requires the geocoder module\nInstall with: sudo pip install geocoder")

try:
    from bs4 import BeautifulSoup
except ImportError:
    exit("This script requires the bs4 module\nInstall with: sudo pip install beautifulsoup4")

# Functions

def shorten(text, length):
    # Process text to be shorter than [length] chars
    str(text)
    if len(text) > length:    
        newtext = ""
        for word in text.split():
            newtext += word[0:4]
            newtext += "."
        return(newtext)
    else:
        return(text)

def degrees_to_cardinal(degrees):
    try:
        cardinal = ["North", "NNE", "NE", "ENE", "East", "ESE", "SE", "SSE",
                "South", "SSW", "SW", "WSW", "West", "WNW", "NW", "NNW"]
        ix = int((degrees + 11.25)/22.5)
        return cardinal[ix % 16]
    except:
        return "Err :("

def get_ip_address(interface):
    try:
        s = subprocess.check_output(["ip","addr","show",interface])
        return s.split('\n')[2].strip().split(' ')[1].split('/')[0]
    except:
        return "Could not find IP address :("

def get_up_stats():
    # Returns a tuple (uptime, 5 min load average)
    try:
        s = subprocess.check_output(["uptime"])
        load_split = s.split('load average: ')
        load_five = float(load_split[1].split(',')[1])
        up = load_split[0]
        up_pos = up.rfind(',',0,len(up)-4)
        up = up[:up_pos].split('up ')[1]
        return ( "UP", up ," L", int(load_five*100),"%" )        
    except:
        return ( '' , 0 )

def get_process_count():
    # Returns the number of processes
    try:
        s = subprocess.check_output(["ps","-e"])
        return len(s.split('\n'))        
    except:
        return 0

def get_temperature():
    try:
        s = subprocess.check_output(["/opt/vc/bin/vcgencmd","measure_temp"])
        return float(s.split('=')[1][:-3])
    except:
        return 0

def get_ram():
    # Returns a tuple (total ram, available ram) in megabytes
    try:
        s = subprocess.check_output(["free","-m"])
        lines = s.split('\n')
        return ( int(lines[1].split()[1]), int(lines[2].split()[3]) )
    except:
        return 0


# Python 2 vs 3 breaking changes
def encode(qs):
    val = ""
    try:
        val = urllib.urlencode(qs).replace("+","%20")
    except:
        val = urllib.parse.urlencode(qs).replace("+", "%20")
    return val


# Command line arguments to set display colour

parser = argparse.ArgumentParser()
parser.add_argument('--colour', '-c', type=str, required=True, choices=["red", "black", "yellow"], help="ePaper display colour")
args = parser.parse_args()

# Set up the display

colour = args.colour
inky_display = InkyPHAT(colour)
inky_display.set_border(inky_display.BLACK)

# Details to customise your weather display

CITY = "Sheffield"
COUNTRYCODE = "GB"
WARNING_TEMP = 25.0

# Convert a city name and country code to latitude and longitude
def get_coords(address):
    g = geocoder.arcgis(address)
    coords = g.latlng
    return coords

# Query Dark Sky (https://darksky.net/) to scrape current weather data
def get_weather(address):
    coords = get_coords(address)
    weather = {}
    res = requests.get("https://darksky.net/forecast/{}/uk212/en".format(",".join([str(c) for c in coords])))
    if res.status_code == 200:
        soup = BeautifulSoup(res.content, "lxml")
        curr = soup.find_all("span", "currently")
        weather["summary"] = curr[0].img["alt"].split()[0]
        weather["temperature"] = int(curr[0].find("span", "summary").text.split()[0][:-1])
        press = soup.find_all("div", "pressure")
        weather["pressure"] = int(press[0].find("span", "num").text)
        return weather
    else:
        return weather

def create_mask(source, mask=(inky_display.WHITE, inky_display.BLACK, inky_display.RED)):
    """Create a transparency mask.
    Takes a paletized source image and converts it into a mask
    permitting all the colours supported by Inky pHAT (0, 1, 2)
    or an optional list of allowed colours.
    :param mask: Optional list of Inky pHAT colours to allow.
    """
    mask_image = Image.new("1", source.size)
    w, h = source.size
    for x in range(w):
        for y in range(h):
            p = source.getpixel((x, y))
            if p in mask:
                mask_image.putpixel((x, y), 255)

    return mask_image

# Dictionaries to store our icons and icon masks in
icons = {}
masks = {}

# Get the weather data for the given location
location_string = "{city}, {countrycode}".format(city=CITY, countrycode=COUNTRYCODE)
weather = get_weather(location_string)

# This maps the weather summary from Dark Sky
# to the appropriate weather icons
icon_map = {
    "snow": ["snow", "sleet"],
    "rain": ["rain"],
    "cloud": ["fog", "cloudy", "partly-cloudy-day", "partly-cloudy-night"],
    "sun": ["clear-day", "clear-night"],
    "storm": [],
    "wind": ["wind"]
}

# Placeholder variables
pressure = 0
temperature = 0
weather_icon = None

if weather:
    temperature = weather["temperature"]
    pressure = weather["pressure"]
    summary = weather["summary"]

    for icon in icon_map:
        if summary in icon_map[icon]:
            weather_icon = icon
            break

else:
    print("Warning, no weather information found!")
    
print ("Processing done")
# Display

font = ImageFont.truetype("/home/pi/Pimoroni/inkyphat/fonts/elec.ttf", 10)
fontsm = ImageFont.truetype("/home/pi/Pimoroni/inkyphat/fonts/elec.ttf", 6)
fontlg = ImageFont.truetype("/home/pi/Pimoroni/inkyphat/fonts/elec.ttf", 16)

inky_display.set_rotation(180)
inkyphat.set_colour('red')
inkyphat.set_border(inkyphat.BLACK)

# Load the backdrop image
inkyphat.set_image("/home/pi/Pimoroni/inkyphat/examples/resources/inkyphat-bg3.png")

# Print text
# Top Left
inkyphat.text((6, 7), datetime, inkyphat.BLACK, font=font)
# Left
inkyphat.text((6, 21), ''.join(map(str, get_up_stats())), inkyphat.BLACK, font=font)
inkyphat.text((6, 31), "T"+str(get_temperature())+"C PR:"+str(get_process_count()), inkyphat.BLACK, font=font)
inkyphat.text((6, 41), 'mb- '.join(map(str, get_ram()))+'mb+', inkyphat.BLACK, font=font)
# Bottom Row
inkyphat.text((6, 87), get_ip_address("wlan0"), inkyphat.WHITE, font=font)
# Right
inkyphat.text((108, 7), u"{:.1f}c".format(temperature)  + " {}mb ".format(pressure) , inkyphat.WHITE if temperature < WARNING_TEMP else inkyphat.RED, font=font)
inkyphat.text((108, 17), pressurestatestr, inkyphat.WHITE, font=font)
inkyphat.text((108, 27), str(windspeed) + "mph " + str(winddir), inkyphat.WHITE, font=font)
inkyphat.text((108, 37), "feels " + u"{:.1f}c ".format(windchill), inkyphat.WHITE, font=font)

inkyphat.line((108, 47, 200, 47), 2) # Red line

inkyphat.text((108, 49), shorten(weathertext0, 14), inkyphat.WHITE, font=font)
inkyphat.text((108, 59), shorten(weathertext1, 14), inkyphat.WHITE, font=font)
inkyphat.text((108, 69), shorten(weathertext2, 14), inkyphat.WHITE, font=font)

inkyphat.show()
print ("Display updated")
