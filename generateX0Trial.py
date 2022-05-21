from psychopy.visual import TextStim
from psychopy import visual, data, event, core, gui, sound
from numpy.random import binomial
import numpy as np
import pandas as pd
import serial
import cedrus_util
from PIL import Image
import pygame


def instructions(win, timer, ser, keymap, part):

    if part == 1:
        instructions = TextStim(win, text = 'Your task is to determine whether a trial is biased towards a majority ' +
                                            'left or right tilted Ts on the screen. After the stimulus with Ts is presented, ' +
                                            'a white fixation will appear where you will either (1) choose to answer by ' +
                                            'pressing the RED button or (2) ask for another sample for more evidence by ' +
                                            'pressing the BLUE button. You should expect to select the BLUE button as you ' +
                                            'more uncertain, and expect to select the RED button when you are confident to ' +
                                            'answer.', pos = (0,0))
    elif part == 2:
        instructions = TextStim(win, text='If the option to answer with the RED button is selected, a black fixation ' +
                                          'will appear. Press the RED button if you believe the trial is biased toward ' +
                                          'majority left T, or press BLUE if you believe the trial is biased toward ' +
                                          'majority right T. Feedback will display in the occurance of an incorrect ' +
                                          ' response.', pos=(0, 0))
    
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


def blockInstructions(win, timer, ser, keymap, block, blocks):
    instructions = TextStim(win, text = 'Block ' + str(block) + '/' + str(blocks) + ' is now finished. To continue, press any button.'
                                         , pos = (0,0))
    
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
            
    return {'Stim Type': 'Block Instructions', 'Start Time (ms)': startTime * 1000,
            'Total Time (ms)': endTime * 1000, 'CEDRUS Total Time (ms)': endTimeCedrus, 'Total Frames': totalFrames}


def generateGridPlacement(n_n, numberOfItems, pixelSpace):
    # will generate a grid of nxn dimensions.
    
    grid = np.array(np.meshgrid(np.linspace(-pixelSpace, pixelSpace, num=n_n), np.linspace(-pixelSpace, pixelSpace, num=n_n))).T.reshape(-1, 2)
    
    # used numberOfItems to select a # of random positions from grid. uniform random.
    positionsGrid = grid[np.random.choice(np.arange(0, n_n ** 2, 1), size = numberOfItems, replace=False),:]
    return positionsGrid.tolist()

    
def generateX0Trial(win, block, trial, totalStimuliDisplay, numberOfItems, probabilityOf0, n_n, itemStimSize,  pixelSpace, stimDuration, frameRate, timer):
    
    positionsGrid = generateGridPlacement(n_n = n_n, numberOfItems = numberOfItems, pixelSpace = pixelSpace)
    
    # 0s are the successes with a probability p of probability Of 0s
    num0s = binomial(n = numberOfItems, p = probabilityOf0)
    numXs = numberOfItems - num0s
    
    stim = []
    for i in range(num0s): # 0(n)
        pos = positionsGrid.pop()
        stim0 = TextStim(win, text = 'T', color =  'white', pos = pos, ori = 45)
        stim.append(stim0)
        
    for i in range(numXs): # 0(n)
        pos = positionsGrid.pop()
        stimX = TextStim(win, text = 'T', color = 'white', pos = pos, ori = -45)
        stim.append(stimX)

    stim.append(visual.ImageStim(win=win, image='./photocell/rect.png', units="pix", pos=(-930,-230))) # photostim
    stim.append(visual.ImageStim(win=win, image='./photocell/rect.png', units="pix", pos=(-930,-110))) # photostim
    screenshot = visual.BufferImageStim(win, stim=stim)
    
    
    totalFrames = round((stimDuration / 1000) * frameRate)
    startTime = timer.getTime()    

    for frame in range(totalFrames): # 0(n)
        screenshot.draw()
        win.flip()
    endTime = timer.getTime() - startTime

    data = {'Block': block, 'Trial': trial, 'totalStimuliDisplay': totalStimuliDisplay, 'Stim Type': 'X0', 'Probability of 0': probabilityOf0, 'Total 0s': num0s, 'Start Time (ms)': startTime * 1000, 'Total Time (ms)': endTime * 1000, 'Total Frames': totalFrames}
    return data


def generateFixationCross(win, ser, keymap, block, trial, probabilityOf0, frameRate, timer, type = 'opt', totalStimuliDisplay = None):
    fixation = TextStim(win, text = '+', pos = (0,0))
    #incorrect = sound.Sound('C')
    
    fixation.height = 50
    
    if type == 'opt':
        fixation.color = 'white'
    elif type == 'response':
        fixation.color = 'black'
        photocell1 = visual.ImageStim(win=win, image='./photocell/rect.png', units="pix", pos=(930,-230)) # photostim
        photocell2 = visual.ImageStim(win=win, image='./photocell/rect.png', units="pix", pos=(930,-110))  # photostim
        photocell1.setAutoDraw(True)
        photocell2.setAutoDraw(True)
    
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
        fixation.setAutoDraw(False)
        if key == [3]:
            penaltyFrameTime = int(0.5 * frameRate)
            for frame in range(penaltyFrameTime): # waits 0.5 seconds before next sample
                win.flip()        
            
            endTime = timer.getTime() - startTime # end time of this fixation period
            totalFrames += penaltyFrameTime # adding the penalty in frames.
        else:
            endTime = reactionTime
        
        data = {'Block': block, 'Trial': trial, 'totalStimuliDisplay': totalStimuliDisplay, 'Stim Type': type, 'Response': key, 'Probability of 0': probabilityOf0, 'Start Time (ms)': startTime * 1000, 'Reaction Time (ms)':  reactionTime * 1000, 'CEDRUS Reaction Time (ms)': reactionTime, 'Reaction Time (frames)': rtFrames, 'Total Time (ms)': endTime * 1000, 'Total Frames': totalFrames}
        
    elif type == 'response':
        photocell1.setAutoDraw(False)
        photocell2.setAutoDraw(False)

        
        if (key == [2] and probabilityOf0 < 0.5) or (key == [3] and probabilityOf0 > 0.5):
            correct = True

        else:
            correct = False
            #incorrect.play()
            incorrectFrameTime = int(0.5 * frameRate)
            fixation.color = 'red'
            for frame in range(incorrectFrameTime): # waits 0.5 seconds before next sample
                win.flip()
            totalFrames += incorrectFrameTime
        fixation.setAutoDraw(False)
        for frame in range(frameRate): # waits 1 second before next trial. The ISI
            win.flip()
        endTime = timer.getTime() - startTime # end time of this fixation presentation.
        totalFrames += frameRate # adding the ISI frames.
            
        data = {'Block': block, 'Trial': trial, 'totalStimuliDisplay': totalStimuliDisplay, 'Stim Type': type, 'Response': key, 'Probability of 0': probabilityOf0, 'Correct': correct, 'Start Time (ms)': startTime * 1000, 'Reaction Time (ms)':  reactionTime * 1000, 'CEDRUS Reaction Time (ms)': reactionTimeCedrus, 'Reaction Time (frames)': rtFrames, 'Total Time (ms)': endTime * 1000, 'Total Frames': totalFrames}
        
    return key, data
    
def trial(win, ser, keymap, block, trial, numberOfItems, n_n, itemStimSize, pixelSpace, probabilities, stimDuration, frameRate, timer):
    probabilityOf0 = probabilities # fixed trial.
    print(probabilityOf0)
    storeData = []
    repeatedStimuli = True
    totalStimuliDisplay = 0
    while repeatedStimuli: # 0(n ^ 2)
        totalStimuliDisplay += 1
                
        data = generateX0Trial(win, block = block, trial = trial, totalStimuliDisplay = totalStimuliDisplay, numberOfItems = numberOfItems, probabilityOf0 = probabilityOf0, n_n = n_n, itemStimSize = itemStimSize,  pixelSpace = pixelSpace, stimDuration = stimDuration, frameRate = frameRate, timer = timer)
        
        storeData.append(data)
        # white fixation: choose to answer or opt out. f to opt, j to skip.
        optOrSkip, data = generateFixationCross(win, ser, keymap, block = block, trial = trial, probabilityOf0 = probabilityOf0, frameRate = frameRate, timer = timer, type = 'opt')
        storeData.append(data)
        
        # black fixation: choose answer.
        if optOrSkip == [2]:
            _, data = generateFixationCross(win, ser, keymap, block = block, trial = trial, probabilityOf0 = probabilityOf0, frameRate = frameRate, timer = timer, type = 'response', totalStimuliDisplay = totalStimuliDisplay)
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
