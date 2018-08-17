#!/usr/bin/env python
import time
import sys
import opc
import RPi.GPIO as GPIO
BRIGHTNESS_BUTTON=23
CYCLE_BUTTON=24

client = opc.Client('localhost:7890')
brightness=256
cycle=0

def brightness_pressed(val):
    global brightness
    brightness = brightness * 4
    if brightness > 256:
        brightness = 1
    print("brightness to %d with %s" % (brightness,val))

def cycle_pressed(val):
    global cycle
    cycle = cycle + 1
    if cycle > 2:
        cycle = 0
    print("cycled to %d with %s" % (cycle,val))

GPIO.setmode(GPIO.BCM)
GPIO.setup([BRIGHTNESS_BUTTON, CYCLE_BUTTON],GPIO.IN)
GPIO.add_event_detect(BRIGHTNESS_BUTTON, GPIO.RISING, callback=brightness_pressed, bouncetime=50)
GPIO.add_event_detect(CYCLE_BUTTON, GPIO.RISING, callback=cycle_pressed, bouncetime=50)

def random_color():
    time.sleep(1)
    from random import randint
    pixels = []
    for x in range(512):
        pixels.append([
            randint(0, 256),
            randint(0, 256),
            randint(0, 256),
        ])
    return pixels

def blank():
    time.sleep(1)
    from random import randint
    pixels = []
    for x in range(512):
        pixels.append([0,0,0])
    return pixels

while True:
    fn = random_color
    if cycle == 0:
        fn = random_color
    elif cycle == 1:
        fn = blank
    client.put_pixels([[((r*brightness)/256.),((g*brightness)/256.),((b*brightness)/256.)] for r,g,b in fn()])
