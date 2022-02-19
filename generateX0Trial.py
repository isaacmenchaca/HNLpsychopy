from psychopy.visual import TextStim
from numpy.random import binomial, uniform
import numpy as np
import random


def generateGridPlacement(n_n, numberOfItems):
    # will generate a grid of nxn dimensions.
    
    # For norm units: chose np.linspace(-0.95, 0.95, num=n) because didnt want shapes on the edge of screen.
    # grid = np.array(np.meshgrid(np.linspace(-0.75, 0.75, num=n_n), np.linspace(-0.75, 0.75, num=n_n))).T.reshape(-1, 2)
    
    # For size=(1920, 1080)
    grid = np.array(np.meshgrid(np.linspace(-250, 250, num=n_n), np.linspace(-250, 250, num=n_n))).T.reshape(-1, 2)
    
    # used numberOfItems to select a # of random positions from grid.
    positionsGrid = grid[np.random.choice(np.arange(0, n_n ** 2, 1), size = numberOfItems, replace=False),:]
    return positionsGrid.tolist()
    
    
def generateX0Trial(win, numberOfItems, probabilityOf0, positionsGrid):
    # 0s are the successes with a probability p of 50%
    num0s = binomial(n = numberOfItems, p = probabilityOf0)
    
    for i in range(num0s - 1): # 0(n)
    # int 0 is red, int 1 is blue, using binomial(1, 0.5)
    # 0 as a Stim.
        pos = positionsGrid.pop()
        stim0 = TextStim(win, text = '0', color =  ['red', 'blue'][binomial(1, 0.5)] , pos = pos)
        stim0.draw()
        
        
    for i in range(numberOfItems - num0s - 1): # 0(n)
        # x as a Stim.
        pos = positionsGrid.pop()
        stimX = TextStim(win, text = 'X', color = ['red', 'blue'][binomial(1, 0.5)], pos = pos)
        stimX.draw()
        
    win.flip()
    return


def generateFixationCross(win, type = 'opt'):
    fixation = TextStim(win, text = '+', pos = (0,0))
    fixation.height = 50
    if type == 'opt':
        fixation.color = 'white'
    elif type == 'response':
        fixation.color = 'black'
    fixation.draw()
    win.flip()
    return
    
    

