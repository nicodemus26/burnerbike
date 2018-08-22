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


# Coordinates of lights in 3-space, with origin at bottom rear of bike.
# +x = right
# +y = top
# +z = front

# produces count-1 pixel positions in 3-space, linearly interpolated
def interp_lights(start, end, count):
    res = []
    current = start
    increment = ((end[0]-float(start[0]))/count, (end[1]-float(start[1]))/count, (end[2]-float(start[2]))/count) 
    for i in range(count-1):
        res.append(current)
        current = (current[0]+increment[0], current[1]+increment[1], current[2]+increment[2])
    return res
        
# Left top
lt = []
lt = lt + interp_lights((8, 15, 12), (8, 14.5, 13), 3)
lt = lt + interp_lights((8, 14.5, 13), (1, 30, 31), 34)
lt = lt + interp_lights((1, 30, 31),  (1, 30, 52.5), 30)

# Bottom
bot = []
bot = bot + interp_lights((0,24,25), (0, 20, 28), 7)
bot = bot + interp_lights((0, 20, 28), (0, 15.5, 29), 8)
bot = bot + interp_lights((0, 15.5, 29), (0, 8.5, 29), 11)
bot = bot + interp_lights((0, 8.5, 29), (0, 8.5, 31.75), 5)
bot = bot + interp_lights((0, 8.5, 31.75), (0, 27.5, 51.75), 38)

# Right top
rt = [(8-x, y, z) for x, y, z in lt]

lightmap = lt+bot+rt
min_x = min(x for x,y,z in lightmap)
min_y = min(y for x,y,z in lightmap)
min_z = min(z for x,y,z in lightmap)
lightmap = [(x-min_x, y-min_y, z-min_z) for x,y,z in lightmap] # re-origin on extreme
max_x = max(x for x,y,z in lightmap)
max_y = max(y for x,y,z in lightmap)
max_z = max(z for x,y,z in lightmap)


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

def map_assist():
    time.sleep(1)
    from random import randint
    pixels = [(256*x/max_x, 256*y/max_y, 256*z/max_z) for x,y,z in lightmap]
    return pixels

def strand_identify():
    time.sleep(1)
    from random import randint
    pixels = ([(255,0,0)]*64)+([(0,255,0)]*64)+([(0,0,255)]*64)
    return pixels

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
        fn = map_assist
    elif cycle == 1:
        fn = blank
    if cycle == 2:
        fn = random_color
    if cycle == 3:
        fn = strand_identify
    client.put_pixels([[((r*brightness)/256.),((g*brightness)/256.),((b*brightness)/256.)] for r,g,b in fn()])
