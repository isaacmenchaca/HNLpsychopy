from psychopy.visual import TextStim
from psychopy import visual, data, event, core, gui
from numpy.random import binomial, uniform
import numpy as np
import random


def instructions(win):
    instructions = TextStim(win, text = 'After stimulus displays, a white fixation will appear. press F to choose to answer or J to skip the trial.\n' +
                                        'If F was selected, a black fixation will appear. This is an indication to select an answer.\n' +
                                        'Press F for majority X, press J for majority 0.' +
                                        'Press any key to start.', pos = (0,0))
    instructions.draw()
    win.flip()
    event.waitKeys(maxWait=float('inf'), modifiers=False, timeStamped=False, clearEvents=True)
    

def generateGridPlacement(n_n, numberOfItems):
    # will generate a grid of nxn dimensions.
    
    # For size=(1920, 1080)
    grid = np.array(np.meshgrid(np.linspace(-250, 250, num=n_n), np.linspace(-250, 250, num=n_n))).T.reshape(-1, 2)
    
    # used numberOfItems to select a # of random positions from grid.
    positionsGrid = grid[np.random.choice(np.arange(0, n_n ** 2, 1), size = numberOfItems, replace=False),:]
    return positionsGrid.tolist()
    
    
def generateX0Trial(win, numberOfItems, probabilityOf0, n_n, stimDuration):
    positionsGrid = generateGridPlacement(n_n = n_n, numberOfItems = numberOfItems)
    # 0s are the successes with a probability p of probabilityOf0%
    num0s = binomial(n = numberOfItems, p = probabilityOf0)
    numXs = numberOfItems - num0s
    
    for i in range(num0s - 1): # 0(n)
    # int 0 is red, int 1 is blue, using binomial(1, 0.5)
    # 0 as a Stim.
        pos = positionsGrid.pop()
        stim0 = TextStim(win, text = '0', color =  ['red', 'blue'][binomial(1, 0.5)] , pos = pos)
        stim0.draw()
        
    
    for i in range(numXs - 1): # 0(n)
        # x as a Stim.
        pos = positionsGrid.pop()
        stimX = TextStim(win, text = 'X', color = ['red', 'blue'][binomial(1, 0.5)], pos = pos)
        stimX.draw()
        
    win.flip()
    core.wait(secs = stimDuration)
    return num0s, numXs


def generateFixationCross(win, type = 'opt'):
    fixation = TextStim(win, text = '+', pos = (0,0))
    fixation.height = 50
    
    if type == 'opt':
        fixation.color = 'white'
    elif type == 'response':
        fixation.color = 'black'
    
    fixation.draw()
    win.flip()
    
    keys = event.waitKeys(maxWait=float('inf'), keyList=['f', 'j'], modifiers=False,
                     timeStamped=False, clearEvents=True)
    print(keys)
    return keys
    
    
def trial(win, numberOfItems, n_n, probVariability, stimDuration):
    # 10 trials just to test stimulus.
    probabilityOf0 = np.random.choice(probVariability, size = 1)[0]
    print(probabilityOf0)
        
    repeatedStimuli = True
        
    while repeatedStimuli:
        # give 300 ms for stimulus presentation.
        num0s, numXs = generateX0Trial(win, numberOfItems = numberOfItems, probabilityOf0 = probabilityOf0, n_n = n_n, stimDuration = stimDuration)
        print(num0s, numXs) # checking observation.
            
        # white fixation: choose to answer or opt out. f to opt, j to skip.
        optOrSkip = generateFixationCross(win, type = 'opt')
            
        # black fixation: choose answer.
        if 'f' in optOrSkip:
            response = generateFixationCross(win, type = 'response')
            # f for 0s, f for Xs.
            print(response)
            repeatedStimuli = False
                
        print(repeatedStimuli)
        # wait 1 second till next trial.
        core.wait(secs = 1)
    return


def informationInputGUI():
    exp_name = 'Letter-Biased Task'
    
    exp_info = {'participant': '',
                'gender:': ('male', 'female'),
                'age': '',
                'left-handed': False}
    dlg = gui.DlgFromDict(dictionary = exp_info, title = exp_name)
    
    exp_info['date'] = data.getDateStr()
    exp_info['exp name'] = exp_name
    
    if dlg.OK == False:
        core.quit() # ends process.
        
        
    return exp_info
