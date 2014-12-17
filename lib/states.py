'''------------------------------------

The game runs on a set of states. Any kind of distinct screen like a 
menu or the game is a state. When states are paused or exited, they 
return a string of the name of the next state or a stop signal. The 
StateManager object handles: 

* State names
* Which states were last executed (the state stack)
* The changing between different states

------------------------------------'''

import pygame, sys

def waitForInput():
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                return

class StateManager(object):
    def __init__(self, initState):
        self.stateIndex = {'game':StateGame(),
                           'main_menu':StateMainMenu(),
                           'options_menu':StateOptionsMenu(),
                           'mode_menu':StateModeMenu()}
        self.currentState = self.init_state(initState)
        self.stateStack = []
    
    def init_state(self, stateName):
        return self.stateIndex[stateName]
                            
    def change_state(self, newState):
        if newState == 'stop':
            pygame.quit()
            quit()
        elif newState == 'last_state':
            try:
                self.currentState = self.stateStack.pop()
            except:
                pass
        else:
            self.stateStack.append(self.currentState)
            self.currentState = self.init_state(newState)
    
    def print_state(self):
        print(self.currentState.name)
        print(self.stateStack)

class State(object):
    def __init__(self):
        self.name = 'state'
    
    def play(self, keyState, time, screen):
        pass
        
class StateGame(State):
    def __init__(self):
        self.name = 'game'
        
    def play(self, keyState, time, screen):
        if keyState.select == True:
            return 'main_menu'
        if keyState.pause == True:
            return 'last_state'
        return None
    
class StateMainMenu(State):
    def __init__(self):
        self.name = 'main_menu'
        
    def play(self, keyState, time, screen):
        if keyState.select == True:
            return 'game'
        if keyState.pause == True:
            return 'last_state'
        return None
        
class StateOptionsMenu(State):
    def __init__(self):
        self.name = 'options_menu'
        
    def play(self, keyState, time, screen):
        if keyState.select == True:
            return 'main_menu'
        return None
        
class StateModeMenu(State):
    def __init__(self):
        self.name = 'mode_menu'
    
    def play(self, keyState, time, screen):
        if keyState.select == True:
            return 'main_menu'
        return None