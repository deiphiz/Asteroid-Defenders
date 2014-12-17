#! python3

'''------------------------------------

This software is licensed under the CC BY-NC-SA 4.0. No warranties are 
included. Please feel free to do whatever you want with this within the 
scope of the license. In fact, I encourage whoever stumbles upon this to
improve on the code... please...

This was the first thing I programmed myself outside of the scope of a 
book or a tutorial, so the code is not exactly the best.

------------------------------------'''
    
import pygame, sys
from lib import states, draw,  input
from pygame.locals import *

WINDOWWIDTH = 800
WINDOWHEIGHT = 600
FPS = 60

pygame.init()
screen = draw.Screen(WINDOWWIDTH, WINDOWHEIGHT)
mainClock = pygame.time.Clock()

stateManager = states.StateManager('main_menu')
keyState = input.KeyState()

#The game loop sends input and tick information to the game state each iteration
#If the state returns a new state, we change it accordingly
def main():
    while True:
        time = mainClock.tick(60)
        keyState.update()
        newState = stateManager.currentState.play(keyState, time, screen)
        if newState:
            stateManager.change_state(newState)

if __name__ == '__main__':
    main()