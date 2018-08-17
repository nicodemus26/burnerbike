#!/usr/bin/env python
import time
import sys
import RPi.GPIO as GPIO
BRIGHTNESS_BUTTON=23
CYCLE_BUTTON=24

brightness=256
cycle=0

def brightness_pressed(val):
    global brightness
    brightness = brightness * 2
    if brightness > 256:
        brightness = 1
    print("brightness to %d with %s" % (brightness,val))

def cycle_pressed(val):
    global cycle
    cycle = cycle + 1
    if cycle > 10:
        cycle = 1
    print("cycled to %d with %s" % (cycle,val))

GPIO.setmode(GPIO.BCM)
GPIO.setup([BRIGHTNESS_BUTTON, CYCLE_BUTTON],GPIO.IN)
GPIO.add_event_detect(BRIGHTNESS_BUTTON, GPIO.RISING, callback=brightness_pressed, bouncetime=50)
GPIO.add_event_detect(CYCLE_BUTTON, GPIO.RISING, callback=cycle_pressed, bouncetime=50)

while True:
    time.sleep(1)
