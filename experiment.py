#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 17 18:43:10 2022

@author: isaacmenchaca
"""
from psychopy import visual, event, core
from generateX0Trial import *


def experiment(numTrials, probVariability):
    # this window size for testing only
    win = visual.Window(size=(1920, 1080), units='pix')
    instructions(win)
    
    
    # 10 trials just to test stimulus.
    for i in range(numTrials):
        probabilityOf0 = np.random.choice(probVariability, size = 1)[0]
        print(probabilityOf0)
        
        # give 300 ms for stimulus presentation.
        num0s, numXs = generateX0Trial(win, numberOfItems = 40, probabilityOf0 = probabilityOf0, n_n = 25, stimDuration = 0.3)
        print(num0s, numXs)
        
        # white fixation: choose to answer or opt out. f to opt, j to skip.
        optOrSkip = generateFixationCross(win, type = 'opt')
        
        # black fixation: choose answer.
        if 'f' in optOrSkip:
            response = generateFixationCross(win, type = 'response')
            # f for 0s, f for Xs.
            print(response)
            
        # wait 1 second till next trial.
        core.wait(secs = 1)

    win.close()
    core.quit()
    return
    
    
experiment(numTrials = 10, probVariability = [0.20, 0.35, 0.50, 0.65, 0.80])
