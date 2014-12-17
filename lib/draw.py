import pygame
from pygame.locals import *

class Screen(object):
    def __init__(self, windowWidth, windowHeight):
        self.windowSurface = pygame.display.set_mode((windowWidth, windowHeight), (HWSURFACE|DOUBLEBUF), 32)
        pygame.display.set_icon(pygame.image.load('assets\\graphics\\player.png'))
        pygame.display.set_caption('Asteroid Defender')
        pygame.mouse.set_visible(False)
        
        self.font = pygame.font.SysFont("OCR A Extended", 24)
        self.titleFont = pygame.font.SysFont("OCR A Extended", 32)
        self.hudFont = pygame.font.SysFont("OCR A Extended", 18)
     
        
    def draw_sprite(surface, rect):
        #We need to make sure the collision box and image align if they are different sizes
        windowSurface.blit(surface, (rect.left - ((surface.get_width() - rect.width) / 2), rect.top - ((surface.get_height() - rect.height) / 2)))