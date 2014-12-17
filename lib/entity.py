import pygame

#load images
playerImage = pygame.image.load('..\\assets\\images\\player.png')
playerHurtImage = pygame.image.load('..\assets\images\\playerhurt.png')
asteroidImage = pygame.image.load('..\assets\images\\asteroid.png')
bgmage = pygame.image.load('..\assets\images\\background.jpg')
laserImage = pygame.image.load('..\assets\images\\laser.png')
explosionFrame1 = pygame.image.load('..\assets\images\\explosion1.png')
explosionFrame2 = pygame.image.load('..\assets\images\\explosion2.png')
baseImage = pygame.image.load('..\assets\images\\spacestation.png')
baseHurtImage = pygame.image.load('..\assets\images\\spacestationhurt.png')

class Entity(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(self)
        
        self.image = pygame.Surface((10, 10)).fill((0,0,0))
        rect = pygame.Rect(0, 0, 10, 10)
        
        self.accelX = 1
        self.accelY = 1
        self.speedX = 0
        self.speedY = 0
        self.maxSpeedX = 1
        self.maxSpeedY = 1
        
    def update(self):
        self.move_ip(self.speedX, self.speedY)
    
    def accelerate(self, dirX, dirY):
        self.speedX += dirX * self.accelX
        if abs(self.speedX) > self.maxSpeedX:
            self.speedX = dirX * self.maxSpeedX
        
        self.speedY += dirY * self.accelY
        if abs(self.speedY) > self.maxSpeedY:
            self.speedY = dirY * self.maxSpeedY