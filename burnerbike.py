#!/usr/bin/env python
import time
import math
import sys
import opc
import RPi.GPIO as GPIO
import hsluv
from opensimplex import OpenSimplex
BRIGHTNESS_BUTTON=23
CYCLE_BUTTON=24

client = opc.Client('localhost:7890')


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
        
# Top to bottom: 3.75"
# Left to right: 12.20"
lightmap = []
for i in range(6):
    for j in range(20):
        #x = (j-10.5)*0.657894737 # 12.5/19
        #y = (i-3.5)*0.76 # 3.8/5
        scale = 2.
        x = -scale+j*(scale*2./19)
        y = -scale+i*(scale*2./5)
        lightmap.append((x,y,0))

min_x = min(x for x,y,z in lightmap)
min_y = min(y for x,y,z in lightmap)
min_z = min(z for x,y,z in lightmap)
max_x = max(x for x,y,z in lightmap)
max_y = max(y for x,y,z in lightmap)
max_z = max(z for x,y,z in lightmap)

for line in range(6):
    vals = ["{: .1f},{: .1f}".format(x, y) for x,y,z in lightmap[line*20:(line+1)*20]]
    print(("".join("{} "*20)).format(*vals))

simplex_a = OpenSimplex(seed=0)
simplex_b = OpenSimplex(seed=1)
simplex_c = OpenSimplex(seed=2)
simplex_scale_x = 0.02
simplex_scale_y = 0.02
simplex_scale_z = 0.02
def simplex_hsl_as_rgb(x, y, z, w):
    x = x * simplex_scale_x
    y = y * simplex_scale_y
    z = z * simplex_scale_z
    h = (simplex_a.noise4d(x, y, z, w)+1)*360
    s = 100-(simplex_b.noise4d(x, y, z, w)+1)*5
    l = 50+(simplex_c.noise4d(x, y, z, w))*5
    r, g, b = hsluv.hsluv_to_rgb([h, s, l])
    return (r*256, g*256, b*256)

def simplex_rgb_as_rgb(x, y, z, w):
    x = x * simplex_scale_x
    y = y * simplex_scale_y
    z = z * simplex_scale_z
    r = (simplex_a.noise4d(x, y, z, w)+1)*128
    g = (simplex_b.noise4d(x, y, z, w)+1)*128
    b = (simplex_c.noise4d(x, y, z, w)+1)*128
    return (r, g, b)

def simplex_hsl():
    #time.sleep(1/60.)
    now = time.time()
    return [simplex_hsl_as_rgb(x, y, z, now*.75) for x,y,z in lightmap]

def random_color():
    #time.sleep(1/60.)
    now = time.time()
    return [simplex_hsl_as_rgb(x*10, y*10, z*10, now*.25) for x,y,z in lightmap]

def simplex_rgb():
    time.sleep(1/60.)
    now = time.time()
    return [simplex_rgb_as_rgb(x, y, z, now*.75) for x,y,z in lightmap]

def map_assist():
    time.sleep(1)
    from random import randint
    pixels = [(256*x/max_x, 256*y/max_y, 256*z/max_z) for x,y,z in lightmap]
    return pixels

def strand_identify():
    time.sleep(.5)
    rgb = [(255,0,0),(0,255,0),(0,0,255)]
    rgbrgbrgbr = (rgb*4)[:10]
    pixels = []
    for i in range(6):
        pixels = pixels+rgbrgbrgbr+([(0,0,0)]*i)+[(128,128,128),(256,256,256)]+([(0,0,0)]*(8-i))
    return pixels

def random_color_per_pixel():
    time.sleep(.5)
    from random import randint
    pixels = []
    for x in range(20*6):
        r, g, b = hsluv.hsluv_to_rgb([randint(0,360), randint(80,101), randint(45,55)])
        pixels.append((r*256, g*256, b*256))
    return pixels

def ripple():
    now = -time.time()
    a = (math.sin(-now*6.28)*6+(now*3.14*2))%360.+math.sin(.25*(now+2)*3.14)
    pixels = []
    center_x = min_x+((max_x-min_x)/2)
    center_y = min_y+((max_y-min_y)/2)
    for x,y,z in lightmap:
        dist = math.sqrt((x-center_y)**2 + (y-center_y)**2)
        off_a = (math.sin((dist+now*3.14)/3.14)**4)
        off_b = (math.sin((dist/10+now*3.14)/3.14)**4)
        h = a+60*off_a-20*off_b+30*(math.sin(-now))
        s = 99 + math.sin(now*3.14/5)*1
        l = 50 + math.sin(now*3.14/15)*5
        r,g,b = [x * 256. for x in hsluv.hsluv_to_rgb([h, s, l])]
        pixels.append((r,g,b))

    return pixels

def blank():
    time.sleep(.5)
    from random import randint
    pixels = []
    for x in range(512):
        pixels.append([0,0,0])
    return pixels

fns = [
        ripple, # 0
        simplex_hsl, # 1
        random_color, # 2
        strand_identify, # 3
        blank, # 4
]

brightness=256.
cycle=0

def brightness_pressed(val):
    global brightness
    brightness = brightness /4.
    if brightness < 4:
        brightness = 256.
    print("brightness to %d with %s" % (brightness,val))

def cycle_pressed(val):
    global cycle
    global fns
    cycle = cycle + 1
    if cycle == len(fns):
        cycle = 0
    print("cycled to %s" % (fns[cycle].__name__))

GPIO.setmode(GPIO.BCM)
GPIO.setup([BRIGHTNESS_BUTTON, CYCLE_BUTTON],GPIO.IN)
GPIO.add_event_detect(BRIGHTNESS_BUTTON, GPIO.RISING, callback=brightness_pressed, bouncetime=200)
GPIO.add_event_detect(CYCLE_BUTTON, GPIO.RISING, callback=cycle_pressed, bouncetime=200)


import random
cycle_time_offset = random.randint(0, 900)
while True:
    now = time.time()
    cycle_time = (now+cycle_time_offset)%900
    if cycle_time < 300:
        cycle = 0
    else:
        if cycle_time % 90 < 30:
            cycle = 1
        else:
            cycle = 2
    fn = fns[cycle]
    dimmed = [[((r*brightness)/256.),((g*brightness)/256.),((b*brightness)/256.)] for r,g,b in fn()]
    clamped = [(int(r), int(g), int(b)) for r,g,b in dimmed]
    client.put_pixels(clamped)
