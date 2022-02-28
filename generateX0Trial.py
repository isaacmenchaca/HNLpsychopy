from psychopy.visual import TextStim
from psychopy import visual, data, event, core, gui
from numpy.random import binomial, uniform
import numpy as np
import random
import pandas as pd


def instructions(win, timer):
    instructions = TextStim(win, text = 'After stimulus displays, a white fixation will appear. press F to choose to answer or J to skip the trial.\n' +
                                        'If F was selected, a black fixation will appear. This is an indication to select an answer.\n' +
                                        'Press F for majority X, press J for majority 0.' +
                                        'Press SPACE key to start.', pos = (0,0))
    
    instructions.setAutoDraw(True)
    keep_going = True
    totalFrames = 0
    startTime = timer.getTime()
    while keep_going:
        totalFrames += 1
        win.flip()
        keys = event.getKeys(keyList=['space'], timeStamped=timer)
        if len(keys) > 0:
            keep_going = False
            
   
    endTime = keys[0][1] - startTime
    instructions.setAutoDraw(False)
            
    return {'Stim Type': 'Instructions', 'Start Time (ms)': startTime * 1000,
            'Total Time (ms)': endTime * 1000, 'Total Frames': totalFrames}



def generateGridPlacement(n_n, numberOfItems):
    # will generate a grid of nxn dimensions.
    
    grid = np.array(np.meshgrid(np.linspace(-250, 250, num=n_n), np.linspace(-250, 250, num=n_n))).T.reshape(-1, 2)
    
    # used numberOfItems to select a # of random positions from grid.
    positionsGrid = grid[np.random.choice(np.arange(0, n_n ** 2, 1), size = numberOfItems, replace=False),:]
    return positionsGrid.tolist()
   
   
   
    
def generateX0Trial(win, trial, numberOfItems, probabilityOf0, n_n, stimDuration, frameRate, timer):
    positionsGrid = generateGridPlacement(n_n = n_n, numberOfItems = numberOfItems)
    # 0s are the successes with a probability p of probability Of 0s
    num0s = binomial(n = numberOfItems, p = probabilityOf0)
    numXs = numberOfItems - num0s
    
    stim = []
    for i in range(num0s - 1): # 0(n)
        pos = positionsGrid.pop()
        stim0 = TextStim(win, text = '0', color =  ['red', 'blue'][binomial(1, 0.5)] , pos = pos)
        stim0.setAutoDraw(True)
        stim.append(stim0)
        
    for i in range(numXs - 1): # 0(n)
        pos = positionsGrid.pop()
        stimX = TextStim(win, text = 'X', color = ['red', 'blue'][binomial(1, 0.5)], pos = pos)
        stimX.setAutoDraw(True)
        stim.append(stimX)
    
    #totalFrames = round((stimDuration / 1000) * frameRate)
    startTime = timer.getTime()
    win.flip()
    core.wait(secs = 0.25)
#    for frame in range(totalFrames): # having a delay problem here ..
#        win.flip()
    endTime = timer.getTime() - startTime
    totalFrames = ((endTime) * frameRate)
    data = {'Trial': trial, 'Stim Type': 'X0', 'Probability of 0': probabilityOf0, 'Total 0s': num0s, 'Start Time (ms)': startTime * 1000, 'Total Time (ms)': endTime * 1000, 'Total Frames': totalFrames}
    
    for item in stim:
        item.setAutoDraw(False)
    
    return data




def generateFixationCross(win, trial, probabilityOf0, frameRate, timer, type = 'opt'):
    fixation = TextStim(win, text = '+', pos = (0,0))
    fixation.height = 50
    
    if type == 'opt':
        fixation.color = 'white'
    elif type == 'response':
        fixation.color = 'black'
    
    fixation.setAutoDraw(True)
    
    startTime = timer.getTime()
    totalFrames = 0
    keep_going = True
    while keep_going:
        totalFrames += 1
        event.clearEvents(eventType='keyboard')
        win.flip()
        keys = event.getKeys(keyList=['f', 'j'], timeStamped=timer)
        if len(keys) > 0:
            keep_going = False
            
    reactionTime = keys[0][1] - startTime
    
    correct = None
    if type == 'opt':
        endTime = reactionTime
    elif type == 'response':
        for frame in range(frameRate): # waits 1 second before next trial. The ISI
            win.flip()
        endTime = timer.getTime() - startTime # end time of this fixation presentation.
        totalFrames += frameRate # adding the ISI frames.
        
        if (keys[0][0] == 'j' and probabilityOf0 > 0.5) or (keys[0][0] == 'f' and probabilityOf0 < 0.5):
            correct = True
        else:
            correct = False
        
    data = {'Trial': trial, 'Stim Type': type, 'Response': keys[0][0], 'Probability of 0': probabilityOf0, 'Correct': correct, 'Start Time (ms)': startTime * 1000, 'Reaction Time (ms)':  reactionTime * 1000, 'Total Time (ms)': endTime * 1000, 'Total Frames': totalFrames}

    fixation.setAutoDraw(False)
    return keys[0][0], data
        
    
    
    
def trial(win, trial, numberOfItems, n_n, probVariability, stimDuration, frameRate, timer):
    # 10 trials just to test stimulus.
    probabilityOf0 = np.random.choice(probVariability, size = 1)[0]
    storeData = []
    repeatedStimuli = True
    while repeatedStimuli:
        data = generateX0Trial(win, trial = trial, numberOfItems = numberOfItems, probabilityOf0 = probabilityOf0, n_n = n_n, stimDuration = stimDuration, frameRate = frameRate, timer = timer)
        storeData.append(data)
            
        # white fixation: choose to answer or opt out. f to opt, j to skip.
        optOrSkip, data = generateFixationCross(win, trial = trial, probabilityOf0 = probabilityOf0, frameRate = frameRate, timer = timer, type = 'opt')
        storeData.append(data)
        
        # black fixation: choose answer.
        if 'f' in optOrSkip:
            _, data = generateFixationCross(win, trial = trial, probabilityOf0 = probabilityOf0, frameRate = frameRate, timer = timer, type = 'response')
            repeatedStimuli = False
            storeData.append(data)
                
    return data['Correct'], storeData




def informationInputGUI():
    exp_name = 'Letter-Biased Task'
    exp_info = {'participant ID': '',
                'gender:': ('male', 'female'),
                'age': '',
                'left-handed': False}
    dlg = gui.DlgFromDict(dictionary = exp_info, title = exp_name)
    exp_info['date'] = data.getDateStr()
    exp_info['exp name'] = exp_name
    
    if dlg.OK == False:
        core.quit() # ends process.
        
    return exp_info




def saveExperimentData(participantInfo, experimentStartTime, experimentEndTime, experimentData):
    participantInfo['Experiment Start Time'] = experimentStartTime
    participantInfo['Experiment End Time'] = experimentEndTime
    participantInfo['Experiment Data'] = experimentData
    df = pd.DataFrame.from_dict(participantInfo)
    csvFileName = participantInfo['participant ID'] + '_' + participantInfo['date'] + '.csv'
    df.to_csv(csvFileName)
    return
