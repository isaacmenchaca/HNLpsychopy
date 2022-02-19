#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 17 18:43:10 2022

@author: isaacmenchaca
"""
from psychopy import visual, event, core
from generateX0Trial import *


def experiment():
    # this window size for testing only
    win = visual.Window(size=(1920, 1080), units='pix')
    
    instructions(win)
    

    # 10 trials just to test stimulus.
    trials = 10
    for i in range(trials):
        positionsGrid = generateGridPlacement(n_n = 25, numberOfItems = 40)
        generateX0Trial(win, numberOfItems = 40, probabilityOf0 = 0.8, positionsGrid = positionsGrid)
        # give 300 ms for stimulus presentation.
        core.wait(secs = 0.3)
        
        # white fixation: choose to answer or opt out.
        generateFixationCross(win, type = 'opt')
        # f to opt, j to skip.
        keys = event.waitKeys(maxWait=float('inf'), keyList=['f', 'j'], modifiers=False,
                     timeStamped=False, clearEvents=True)
        print(keys)
        
        # black fixation: choose answer.
        if 'f' in keys:
            generateFixationCross(win, type = 'response')
            # f for 0s, f for Xs.
            response = event.waitKeys(maxWait=float('inf'), keyList=['f', 'j'], modifiers=False, timeStamped=False, clearEvents=True)
            print(response)
            
        # wait 1 second till next trial.
        core.wait(secs = 1)


    win.close()
    core.quit()
    return
    
    
experiment()
