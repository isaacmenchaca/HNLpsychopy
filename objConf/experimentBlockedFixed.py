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
import os



# run over 100 times for 
def experiment(participantInfo, numTrials, blocks, probabilities, numberOfItems, itemStimSize, n_n, pixelSpace, stimDuration, dataPath, numCorrectToEnd = None):
    
    if ((blocks * numTrials) % len(probabilities) != 0) or (blocks * numTrials < numCorrectToEnd):
        core.quit()
    
    fixedEqualNumOccurance = int((blocks * numTrials) / len(probabilities))
    allProbabiltiesForTrials = (np.ones([fixedEqualNumOccurance, len(probabilities)]) * np.array(probabilities)).ravel()# Fixed
    np.random.shuffle(allProbabiltiesForTrials) # Fixed
    allProbabiltiesForTrials = allProbabiltiesForTrials.reshape([blocks, numTrials]) # fixed
    
    
    # participantInfo = informationInputGUI()
    
    
    # get portname -- paste Jennys Code.
    portname, keymap = cedrus_util.getname()
    ser = serial.Serial(portname, 115200) 


    win = visual.Window(size=(1920, 1080), units='pix', fullscr = True)
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
    experimentData.append(instructions(win, timer, ser, keymap, 3))

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

        experimentEndTime = timer.getTime() * 1000
        saveExperimentData(participantInfo, experimentStartTime, experimentEndTime, experimentData, blk, dataPath)

        if numCorrectToEnd != None and numCorrectToEnd == 0:
            experimentData.append(instructions(win, timer, ser, keymap, -1))
            break
        else:
            experimentData.append(blockInstructions(win, timer, ser, keymap, blk + 1, blocks))

    
    win.close()
    
    print('Overall, %i frames were dropped.' % win.nDroppedFrames)
    core.quit()
    return

if __name__ == '__main__':
    participantInfo = informationInputGUI()

    currentPath = os.getcwd()
    path = os.path.join(currentPath, 'data/' + participantInfo['Participant ID'] + 'Session' + participantInfo['Session'])
    os.mkdir(path)

    if participantInfo['practice?'] == True:
        experiment(participantInfo=participantInfo, numTrials=10, blocks=4, numCorrectToEnd=15,
                   probabilities=[0.4, 0.425, 0.575, 0.6], numberOfItems=40,
                   itemStimSize=25, n_n=10, pixelSpace=125,
                   stimDuration=400, dataPath = path)

    else:
        experiment(participantInfo=participantInfo, numTrials = 50, blocks = 4, numCorrectToEnd = 150,
                   probabilities = [0.4, 0.425, 0.575, 0.6], numberOfItems = 40,
                   itemStimSize = 25, n_n = 10,  pixelSpace = 125,
                   stimDuration = 400, dataPath = path)

# numTrials: number of trials per block.

# numberOfItems: total X and 0s in grid.
# n_n: a value n which determines an nxn grid.
# probVariability: the biased probability towards 0 in a bernoulli process.
# stimDuration: seconds to display stimulus.   
    
    


