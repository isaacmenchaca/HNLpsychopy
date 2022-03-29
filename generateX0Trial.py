from psychopy.visual import TextStim
from psychopy import visual, data, event, core, gui
from numpy.random import binomial
import numpy as np
import pandas as pd
import serial
import cedrus_util



def instructions(win, timer, ser, keymap):
    instructions = TextStim(win, text = 'After stimulus displays, a white fixation will appear. Press RED to answer or BLUE to skip the trial.\n\n' +
                                        'If RED was selected, a black fixation will appear. This is a queue to give an answer.\n' +
                                        'Press RED if the trial is biased toward majority X, or press BLUE for majority 0. ' +
                                        'Press any button to start.', pos = (0,0))
    
    instructions.setAutoDraw(True)
    keep_going = True
    totalFrames = 0
    startTime = timer.getTime()
    cedrus_util.reset_timer(ser)    # reset responsebox timer
    keylist = []
    while keep_going:
        totalFrames += 1
        win.flip()
        receiveBuffer = ser.in_waiting
        
        if receiveBuffer != 0:
            endTimer = timer.getTime()
            keylist.append(ser.read(ser.in_waiting))
            key, press, time = cedrus_util.readoutput([keylist[-1]], keymap)
            if key and press == [1]:
                break
    
    endTime = endTimer - startTime
    # convert the time of correct button push
    endTimeCedrus = cedrus_util.HexToRt(cedrus_util.BytesListToHexList(time))
   
    
    instructions.setAutoDraw(False)
            
    return {'Stim Type': 'Instructions', 'Start Time (ms)': startTime * 1000,
            'Total Time (ms)': endTime * 1000, 'CEDRUS Total Time (ms)': endTimeCedrus, 'Total Frames': totalFrames}



def generateGridPlacement(n_n, numberOfItems):
    # will generate a grid of nxn dimensions.
    
    grid = np.array(np.meshgrid(np.linspace(-250, 250, num=n_n), np.linspace(-250, 250, num=n_n))).T.reshape(-1, 2)
    
    # used numberOfItems to select a # of random positions from grid. uniform random.
    positionsGrid = grid[np.random.choice(np.arange(0, n_n ** 2, 1), size = numberOfItems, replace=False),:]
    return positionsGrid.tolist()
   
   
   
    
def generateX0Trial(win, trial, totalStimuliDisplay, numberOfItems, probabilityOf0, n_n, stimDuration, frameRate, timer):
    positionsGrid = generateGridPlacement(n_n = n_n, numberOfItems = numberOfItems)
    # 0s are the successes with a probability p of probability Of 0s
    num0s = binomial(n = numberOfItems, p = probabilityOf0)
    numXs = numberOfItems - num0s
    
    stim = []
    for i in range(num0s - 1): # 0(n)
        pos = positionsGrid.pop()
        stim0 = TextStim(win, text = '0', color =  'white', pos = pos)
        stim.append(stim0)
        
    for i in range(numXs - 1): # 0(n)
        pos = positionsGrid.pop()
        stimX = TextStim(win, text = 'X', color = 'white', pos = pos)
        stim.append(stimX)
    
    screenshot = visual.BufferImageStim(win, stim=stim)
    
    totalFrames = round((stimDuration / 1000) * frameRate)
    startTime = timer.getTime()

    for frame in range(totalFrames): # 0(n)
        screenshot.draw()
        win.flip()
    endTime = timer.getTime() - startTime

    data = {'Trial': trial, 'totalStimuliDisplay': totalStimuliDisplay, 'Stim Type': 'X0', 'Probability of 0': probabilityOf0, 'Total 0s': num0s, 'Start Time (ms)': startTime * 1000, 'Total Time (ms)': endTime * 1000, 'Total Frames': totalFrames}
    
    return data




def generateFixationCross(win, ser, keymap, trial, probabilityOf0, frameRate, timer, type = 'opt', totalStimuliDisplay = None):
    fixation = TextStim(win, text = '+', pos = (0,0))
    fixation.height = 50
    
    if type == 'opt':
        fixation.color = 'white'
    elif type == 'response':
        fixation.color = 'black'
    
    fixation.setAutoDraw(True)
    
    keep_going = True
    startTime = timer.getTime()
    cedrus_util.reset_timer(ser)    # reset responsebox timer
    totalFrames = 0
    keylist = []
    
    cedrus_util.clear_buffer(ser)
    while keep_going: # 0(n)
        totalFrames += 1
        
        win.flip()
        receiveBuffer = ser.in_waiting
        
        if receiveBuffer >= 6:
            reactionTimer = timer.getTime()
            keylist.append(ser.read(ser.in_waiting))
            key, press, time = cedrus_util.readoutput([keylist[-1]], keymap)
            if press == [1] and (key == [2] or key == [3]):
                keep_going = False
        cedrus_util.clear_buffer(ser)    
    
    reactionTime = reactionTimer - startTime
    # convert the time of correct button push
    reactionTimeCedrus = cedrus_util.HexToRt(cedrus_util.BytesListToHexList(time))
    rtFrames = totalFrames
    
    
    
    data = None
    correct = None
    if type == 'opt':
        endTime = reactionTime
        data = {'Trial': trial, 'totalStimuliDisplay': totalStimuliDisplay, 'Stim Type': type, 'Response': key, 'Probability of 0': probabilityOf0, 'Start Time (ms)': startTime * 1000, 'Reaction Time (ms)':  reactionTime * 1000, 'CEDRUS Total Time (ms) Reaction Time (ms)': reactionTime, 'Reaction Time (frames)': rtFrames, 'Total Time (ms)': endTime * 1000, 'Total Frames': totalFrames}
        
    elif type == 'response':
        for frame in range(frameRate): # waits 1 second before next trial. The ISI
            win.flip()
        endTime = timer.getTime() - startTime # end time of this fixation presentation.
        totalFrames += frameRate # adding the ISI frames.
        
        if (key == [2] and probabilityOf0 < 0.5) or (key == [3] and probabilityOf0 > 0.5):
            correct = True
        else:
            correct = False
            
        data = {'Trial': trial, 'totalStimuliDisplay': totalStimuliDisplay, 'Stim Type': type, 'Response': key, 'Probability of 0': probabilityOf0, 'Correct': correct, 'Start Time (ms)': startTime * 1000, 'Reaction Time (ms)':  reactionTime * 1000, 'CEDRUS Reaction Time (ms)': reactionTimeCedrus, 'Reaction Time (frames)': rtFrames, 'Total Time (ms)': endTime * 1000, 'Total Frames': totalFrames}
        
    

    fixation.setAutoDraw(False)
    return key, data
        
    
    
    
def trial(win, ser, keymap, trial, numberOfItems, n_n, probVariability, stimDuration, frameRate, timer):
    probabilityOf0 = np.random.choice(probVariability, size = 1)[0]
    storeData = []
    repeatedStimuli = True
    totalStimuliDisplay = 0
    while repeatedStimuli: # 0(n ^ 2)
        totalStimuliDisplay += 1
        data = generateX0Trial(win, trial = trial, totalStimuliDisplay = totalStimuliDisplay, numberOfItems = numberOfItems, probabilityOf0 = probabilityOf0, n_n = n_n, stimDuration = stimDuration, frameRate = frameRate, timer = timer)
        storeData.append(data)
        # white fixation: choose to answer or opt out. f to opt, j to skip.
        optOrSkip, data = generateFixationCross(win, ser, keymap, trial = trial, probabilityOf0 = probabilityOf0, frameRate = frameRate, timer = timer, type = 'opt')
        storeData.append(data)
        
        # black fixation: choose answer.
        if optOrSkip == [2]:
            _, data = generateFixationCross(win, ser, keymap, trial = trial, probabilityOf0 = probabilityOf0, frameRate = frameRate, timer = timer, type = 'response', totalStimuliDisplay = totalStimuliDisplay)
            repeatedStimuli = False
            storeData.append(data)

               
    return data['Correct'], storeData




def informationInputGUI():
    exp_name = 'Letter-Biased Task'
    exp_info = {'Participant ID': '',
    		'Session': ('1', '2'),
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
    csvFileName = participantInfo['Participant ID'] + '_' + participantInfo['date'] + '.csv'
    df.to_csv(csvFileName)
    return
