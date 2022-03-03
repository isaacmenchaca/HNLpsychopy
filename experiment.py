#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 17 18:43:10 2022

@author: isaacmenchaca
"""
from psychopy import visual, event, core, logging
from generateX0Trial import *
import pandas as pd
import serial
import cedrus_util




def experiment(numTrials, probVariability):
    
    participantInfo = informationInputGUI()
    
    
    # get portname -- paste Jennys Code.
    portname, keymap = cedrus_util.getname()
    ser = serial.Serial(portname, 115200) 


    win = visual.Window(size=(1920, 1080), units='pix')
    logging.console.setLevel(logging.WARNING)  #this will print if there is a delay
    win.recordFrameIntervals = True    
    win.refreshThreshold = 1/60 + 0.004
    frameRate = round(win.getActualFrameRate())
    
    cedrus_util.reset_timer(ser)    # reset responsebox timer
    timer = core.Clock()
    experimentStartTime = timer.getTime() * 1000
    
    experimentData = []
    experimentData.append(instructions(win, timer, ser, keymap))
    for i in range(numTrials):
        # numberOfItems: total X and 0s in grid.
        # n_n: a value n which determines an nxn grid.
        # probVariability: the biased probability towards 0 in a bernoulli process.
        # stimDuration: seconds to display stimulus.
        print(i)
        correct = False
        while not correct:
            correct, data = trial(win, ser, keymap, trial = i, numberOfItems = 40, n_n = 25, probVariability = probVariability, stimDuration = 250, frameRate = frameRate, timer = timer)
            print(correct)
            experimentData += data

    experimentEndTime = timer.getTime() * 1000
    
    saveExperimentData(participantInfo, experimentStartTime, experimentEndTime, experimentData)
    
    win.close()
    
    print('Overall, %i frames were dropped.' % win.nDroppedFrames)
    core.quit()
    return
    
    
#experiment(numTrials = 5, probVariability = [0.20, 0.35, 0.45, 0.55, 0.65, 0.80])

experiment(numTrials = 5, probVariability = [0.01, .99])
