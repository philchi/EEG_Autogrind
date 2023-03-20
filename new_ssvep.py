import pygame as pg
import time as t
import numpy as np
import scipy.signal as signal
import pylsl
import autotrain as auto

# Initializing visual stimuli params
flashDur = 2    # duration of a flashing period (s)
pause = 1       # pause duration between each flashing period (s)

# init visual stimuli state at each frame
refresh_rate = 60.0
indices = np.arange(0, 60)

ind8 = signal.square(2 * np.pi * 8 * (indices / refresh_rate))
ind8 = (ind8 + 1) / 2

ind10 = signal.square(2 * np.pi * 10 * (indices / refresh_rate))
ind10 = (ind10 + 1) / 2

ind12 = signal.square(2 * np.pi * 12 * (indices / refresh_rate))
ind12 = (ind12 + 1) / 2

ind14 = signal.square(2 * np.pi * 14 * (indices / refresh_rate))
ind14 = (ind14 + 1) / 2

# mapping markers to character movements
markers = {'left': auto.forwardl, 'up': auto.jumpAtt, 'down': auto.drop, 'right': auto.forwardr}

def get_input(marker):
    for m in markers:
        if marker == m:
            return markers[m]
    return auto.forwardr

def createMrkStream(name):
    info = pylsl.stream_info(name, 'Markers', 1, 0, pylsl.cf_string, 'unsampledStream')
    outlet = pylsl.stream_outlet(info, 1, 1)
    return outlet

def lsl_inlet(name):
    inlet = None
    info = pylsl.resolve_stream('name', name)
    inlet = pylsl.stream_inlet(info[0], recover=0)
    return inlet

# Initializing outlet and inlet streams
mrkstream = createMrkStream('SSVEP_Markers')
resultstream = lsl_inlet('egg_res')

# Initializing Pygame
pg.init()
 
# Initializing surface
surface = pg.display.set_mode((1400,800))
 
# Initializing clock for setting frame rate
clock = pg.time.Clock()

# Initializing loop params (frame counter, timer, etc.)
frameN = 0
sec = -1
route = []          # list of movements to be executed during automation
sentMrk = False     # whether a 'pause' marker has been sent
playStim = False    # play visual stimuli
playAuto = False    # auto play MS
r_ind = 0           # index of movement list

while True:
    events = pg.event.get()
    for event in events:
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_p:
                playAuto = False

                if playStim == False:
                    route = []

                playStim = not playStim
                frameN = 0
                sec = -1
                sentMrk = False

            if event.key == pg.K_a:
                playStim = False
                playAuto = not playAuto
                r_ind = 0

        if event.type == pg.QUIT:
            mrkstream.push_sample(pylsl.vectorstr(['die']))
            pg.quit()
            exit()

    if playStim:
        currFrame = frameN % 60         # returns the frame number out of 60 frames
        inPause = sec >= flashDur       # returns 1 if during pause time, and 0 otherwise
        res, t_res = resultstream.pull_sample(timeout=0)

        pg.draw.rect(surface, (255*max(ind8[currFrame], inPause), 0, 0), pg.Rect(20, 20, 180, 180))     # 8Hz (top left)
        pg.draw.rect(surface, (255*max(ind10[currFrame], inPause), 0, 0), pg.Rect(1200, 20, 180, 180))  # 10Hz (top right)
        pg.draw.rect(surface, (255*max(ind12[currFrame], inPause), 0, 0), pg.Rect(20, 600, 180, 180))   # 12Hz (bot left)
        pg.draw.rect(surface, (255*max(ind14[currFrame], inPause), 0, 0), pg.Rect(1200, 600, 180, 180)) # 14Hz (bot right)

        if inPause:                     # in pausing period
            if res != None:
                print('added')
                route.append(get_input(res[0]))
                added = True
            if not sentMrk:
                mrkstream.push_sample(pylsl.vectorstr(['pause']))
                sentMrk = True
        if currFrame == 0:              # end of a second
            sec += 1
            print(route)
        if sec == flashDur + pause:     # end of a flashing + pausing period  
            sec = 0
            added = False
            sentMrk = False
        if sec == 0:                    # start of a flashing period
            mrkstream.push_sample(pylsl.vectorstr(['start']))
        
    else:
        pg.draw.rect(surface, (255, 0, 0), pg.Rect(20, 20, 180, 180))    # 8Hz
        pg.draw.rect(surface, (255, 0, 0), pg.Rect(1200, 20, 180, 180))  # 10Hz
        pg.draw.rect(surface, (255, 0, 0), pg.Rect(20, 600, 180, 180))   # 12Hz
        pg.draw.rect(surface, (255, 0, 0), pg.Rect(1200, 600, 180, 180)) # 14Hz

    pg.display.update()

    if playAuto:
        try:
            route[r_ind]()
            r_ind += 1
            
            if r_ind == len(route):
                r_ind = 0
        except:
            print('No actions queued')

    frameN += 1
    clock.tick(refresh_rate)
    #print(clock.get_fps())