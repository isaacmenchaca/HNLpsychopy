#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 17 18:43:10 2022

@author: isaacmenchaca
"""
from psychopy import visual, core, logging
from generateX0Trial import informationInputGUI, instructions, trial, saveExperimentData, blockInstructions
import pandas as pd
import numpy as np
import serial
import cedrus_util



# run over 100 times for 
def experiment(numTrials, blocks, probabilities, numberOfItems, itemStimSize, n_n, pixelSpace, stimDuration, numCorrectToEnd = None):
    
    if (blocks * numTrials) % len(probabilities) != 0:
        core.quit()
    
    fixedEqualNumOccurance = int((blocks * numTrials) / len(probabilities))
    allProbabiltiesForTrials = (np.ones([fixedEqualNumOccurance, len(probabilities)]) * np.array(probabilities)).ravel()# Fixed
    np.random.shuffle(allProbabiltiesForTrials) # Fixed
    allProbabiltiesForTrials = allProbabiltiesForTrials.reshape([blocks, numTrials]) # fixed
    
    
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
    experimentData.append(instructions(win, timer, ser, keymap, 1))
    experimentData.append(instructions(win, timer, ser, keymap, 2))

    for blk in range(blocks):
        for i in range(numTrials):
            print('block:', blk, ' trial:', i, ':')
            correct, data = trial(win, ser, keymap, block = blk, trial = i, numberOfItems = numberOfItems, n_n = n_n, itemStimSize = itemStimSize, pixelSpace = pixelSpace, probabilities= allProbabiltiesForTrials[blk, i], stimDuration = stimDuration, frameRate = frameRate, timer = timer)
            print(correct)
            experimentData += data

            if numCorrectToEnd != None and correct:
                numCorrectToEnd -= 1
            if numCorrectToEnd != None and numCorrectToEnd == 0:
                break
    
        experimentData.append(blockInstructions(win, timer, ser, keymap, blk + 1, blocks))


    experimentEndTime = timer.getTime() * 1000
    saveExperimentData(participantInfo, experimentStartTime, experimentEndTime, experimentData)
    
    win.close()
    
    print('Overall, %i frames were dropped.' % win.nDroppedFrames)
    core.quit()
    return
    

experiment(numTrials = 8, blocks = 1, numCorrectToEndToEnd = None,
           probabilities = [.40, 0.425, 0.575, 0.60], numberOfItems = 40,
           itemStimSize = 25, n_n = 10,  pixelSpace = 125,
           stimDuration = 250)
                                                                                                     
# numberOfItems: total X and 0s in grid.
# n_n: a value n which determines an nxn grid.
# probVariability: the biased probability towards 0 in a bernoulli process.
# stimDuration: seconds to display stimulus.   
    
    


