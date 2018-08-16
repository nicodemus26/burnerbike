#!/usr/bin/env python
import time
import sys
import RPi.GPIO as GPIO
BUTTON_GPIO=23

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_GPIO,GPIO.IN)

#initialise a previous input variable to 0 (assume button not pressed last)
i = 0
prev_input = 0
while True:
  #take a reading
  input = GPIO.input(BUTTON_GPIO)
  #if the last reading was low and this one high, print
  if ((not prev_input) and input):
    time.sleep(0.02) # make sure this is not a transient click, poll again right after
    input = GPIO.input(BUTTON_GPIO)
    if ((not prev_input) and input):
      print("Button pressed %d" % (i,))
      i = i + 1
  #update previous input
  prev_input = input
  #slight pause to debounce
  time.sleep(0.05)
