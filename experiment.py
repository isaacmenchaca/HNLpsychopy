#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 17 18:43:10 2022

@author: isaacmenchaca
"""
from psychopy import visual, event, core
from generateX0Trial import *


def experiment(numTrials, probVariability):

    idk = informationInputGUI()
    print(type(idk))

    win = visual.Window(size=(1920, 1080), units='pix')
    instructions(win)
    
    # 10 trials just to test stimulus.
    for i in range(numTrials):
        trial(win, numberOfItems = 40, n_n = 25, probVariability = probVariability, stimDuration = 0.3)

    win.close()
    core.quit()
    return
    
    
experiment(numTrials = 3, probVariability = [0.20, 0.35, 0.45, 0.55, 0.65, 0.80])
