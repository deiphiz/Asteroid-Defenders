import pygame, configparser
from pygame.locals import *

#Get key bindings from ini
settings = configparser.RawConfigParser()
settings.read('settings.ini')
PAUSE = eval(settings.get('Bindings', 'Pause'))
LEFT = eval(settings.get('Bindings', 'Left'))
RIGHT = eval(settings.get('Bindings', 'Right'))
UP = eval(settings.get('Bindings', 'Up'))
DOWN = eval(settings.get('Bindings', 'Down'))
SHOOT = eval(settings.get('Bindings', 'Shoot'))
SELECT = eval(settings.get('Bindings', 'Select'))

class KeyState(object):
    def __init__(self):
        self.pause = False
        self.xDir = 0
        self.yDir = 0
        self.trigger = False
        self.select = False
        
        self.pressed = pygame.key.get_pressed()
        
    def update(self):
        self.reset()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                quit()
        self.pressed = pygame.key.get_pressed()
        if self.pressed[PAUSE]:
            self.pause = True
        self.xDir = self.pressed[RIGHT] - self.pressed[LEFT]
        self.yDir = self.pressed[DOWN] - self.pressed[UP]
        if self.pressed[SHOOT]:
            self.trigger = True
        if self.pressed[SELECT]:
            self.select = True
    
    def reset(self):
        self.pause = False
        self.xDir = 0
        self.yDir = 0
        self.trigger = False
        self.select = False
            
    def print_self(self):
        print('''
        pause: %s
        xDir: %s
        yDir: %s
        trigger: %s
        select: %s
        ''' % (self.pause, self.xDir, self.yDir, self.trigger, self.select))