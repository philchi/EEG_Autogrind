import pydirectinput as pd
import sys
import time as t
import random as r

jump = 'space'
att1 = 'e'
att2 = 'q'

pd.FAILSAFE = True
kStack = {}

def countdown(mins = 0.07):
    global timer
    timer = mins * 60

    while timer > 0:
        t.sleep(1)
        timer -= 1

def keyDown(key):
    pd.keyDown(key)
    kStack[key] = 1

def keyUp(key):
    pd.keyUp(key)
    kStack[key] = 0

def stop():
    pd.FAILSAFE = False
    for key in kStack:
        if kStack[key] == 1:
            keyUp(key)
            print(f"reset '{key}'")

    sys.exit()

def attack():
    pd.press(att1)
    pd.press(att2)

def dashAtt():               # dash attack
    sgap = r.randint(13, 16) / 1000

    pd.PAUSE = 0.05
    pd.press(jump)
    keyDown(jump)
    pd.PAUSE = 0.1
    t.sleep(sgap)
    attack()
    t.sleep(0.03)
    keyUp(jump)

def DdashAtt():              # double dash attack
    sgap = r.randint(13, 16) / 1000

    pd.PAUSE = 0.05
    pd.press(jump)
    pd.press(jump)
    keyDown(jump)
    pd.PAUSE = 0.1
    t.sleep(sgap)
    attack()
    t.sleep(0.03)
    keyUp(jump)

def forwardr(cycles = 2):
    sgap = r.randint(20, 22) / 1000

    keyDown('right')
    for i in range(cycles):
        dashAtt()
        t.sleep(sgap)
    keyUp('right')

def forwardl(cycles = 2):
    sgap = r.randint(20, 22) / 1000

    keyDown('left')
    for i in range(cycles):
        dashAtt()
        t.sleep(sgap)
    keyUp('left')

def drop(cycles = 1):
    lgap = r.randint(194, 234) / 1000
    sgap = r.randint(11, 25) / 1000

    for i in range(cycles):
        keyDown('down')
        keyDown('space')
        t.sleep(sgap)
        keyUp('space')
        keyUp('down')
        t.sleep(lgap)

def jumpAtt():
    lgap = r.randint(200, 213) / 1000
    mgap = r.randint(52, 87) / 1000

    pd.PAUSE = 0.05
    pd.press(jump)
    keyDown('up')
    pd.press(jump)
    pd.PAUSE = 0.1
    keyUp('up')
    t.sleep(lgap)
    attack()
    t.sleep(mgap)