import pygame, random, sys, copy
from pygame.locals import *

WINDOWWIDTH = 800
WINDOWHEIGHT = 600
FPS = 30
TEXTCOLOR = (100, 255, 100)
EXPLOSIONTEXTCOLOR = (255, 255, 255)
BACKGROUNDCOLOR = (0, 0, 0)
BULLETSPEED = 20 # I wouldn't set this any higher than BADDIECOLLISION
BULLETRATE = 8 # Setting this too low causes the program to crash when firing large barrages of bullets. Not sure why yet.
MAXBULLETS = 20
BADDIESIZE = 90
BADDIECOLLISION = 45 # Remember that setting this lower will reduce stupid player collision, but will also make baddies harder to hit
PLAYERCOLLISION = 45 # Also don't set these higher than the size of the player/baddies or the collision box will be OUTSIDE the sprite
BADDIEMINSPEED = 3
BADDIEMAXSPEED = 9
MAXBADDIES = 20
EXPLOSIONSIZE = 48
BACKGROUNDSCROLLRATE = 1
DIFFICULTY = (30, 3) #First is initial rate of spawn, second is how much is subtracted when moving to next level
PLAYERACCEL = 1
PLAYERDEACCEL = 1
MAXSPEED = 16

def terminate():
	pygame.quit()
	sys.exit()

def waitForPlayerToPressKey():
	while True:
		for event in pygame.event.get():
			if event.type == QUIT:
				terminate()
			if event.type == KEYDOWN:
				if event.key == K_ESCAPE: # pressing escape quits
					terminate()
				return

def playerHasHitBaddie(playerRect, baddies):
	for b in baddies:
		if playerRect.colliderect(b['rect']):
			return True
	return False

def drawText(text, font, color, surface, x, y):
	textobj = font.render(text, 1, color)
	textrect = textobj.get_rect()
	textrect.topleft = (x, y)
	surface.blit(textobj, textrect)

# set up pygame, the window, and the mouse cursor
pygame.init()
mainClock = pygame.time.Clock()
windowSurface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), (HWSURFACE|DOUBLEBUF), 32)
pygame.display.set_icon(pygame.image.load('data\\player.png'))
pygame.display.set_caption('EPIC SPACE SHOOTER')
pygame.mouse.set_visible(False)

# set up font
font = pygame.font.SysFont("OCR A Extended", 30)

# set up sounds
gameOverSound = pygame.mixer.Sound('data\\gameover.wav')
laserSound = pygame.mixer.Sound('data\\laser.wav')
explosionSound = pygame.mixer.Sound('data\\explosion.wav')
explosionSound.set_volume(0.7)
pygame.mixer.music.load('data\\music.ogg')

# set up images
playerImage = pygame.image.load('data\\player.png')
playerRect = pygame.Rect(0, 0, PLAYERCOLLISION, PLAYERCOLLISION)
baddieImage = pygame.image.load('data\\baddie.png')
background = pygame.image.load('data\\background.jpg')
backgroundRect = pygame.Rect(0, 0, WINDOWWIDTH, WINDOWHEIGHT)
backgroundScaled = pygame.transform.scale(background, (WINDOWWIDTH, WINDOWHEIGHT))
laserImage = pygame.image.load('data\\laser.png')
explosionFrame1 = pygame.image.load('data\\explosion1.png')
explosionFrame1Scaled = pygame.transform.scale(explosionFrame1, (EXPLOSIONSIZE, EXPLOSIONSIZE))
explosionFrame2 = pygame.image.load('data\\explosion2.png')
explosionFrame2Scaled = pygame.transform.scale(explosionFrame2, (EXPLOSIONSIZE, EXPLOSIONSIZE))

# show the "Start" screen
windowSurface.blit(backgroundScaled, (0, 0))
drawText('EPIC SPACE SHOOTER', font, TEXTCOLOR, windowSurface, 20, (WINDOWHEIGHT / 3))
drawText('Use the arrow keys to move,', font, TEXTCOLOR, windowSurface, 20, (WINDOWHEIGHT / 3) + 40)
drawText('Press the spacebar to shoot! ', font, TEXTCOLOR, windowSurface, 20, (WINDOWHEIGHT / 3) + 80)
drawText('Press any key to start...', font, TEXTCOLOR, windowSurface, 20, (WINDOWHEIGHT / 3) + 120)
pygame.display.update()
waitForPlayerToPressKey()

# Set up player movement variables
playerSpeedX = 0
playerSpeedY = 0
dirX = 0
dirY = 0
accelx = False
accely = False


topScore = 0
while True:
	# set up the start of the game
	baddies = []
	bullets = []
	backgroundList = []
	killedBaddies = []
	trigger = False
	score = 0
	kills = 0
	toNextLevel = 1
	playerRect.topleft = (WINDOWWIDTH / 2, WINDOWHEIGHT - 50)
	moveLeft = moveRight = moveUp = moveDown = False
	reverseCheat = slowCheat = False
	baddieAddCounter = 0
	addNewBaddieRate = DIFFICULTY[0]
	bulletCounter = BULLETRATE - 1
	pygame.mixer.music.play(-1, 0.0)
	endName = 1
	debug = False

	while True: # the game loop runs while the game part is playing
		score += 1 # increase score

		for event in pygame.event.get():
			if event.type == QUIT:
				terminate()

			if event.type == KEYDOWN:
				if event.key == ord('z'):
					reverseCheat = True
				if event.key == ord('x'):
					slowCheat = True
				if event.key == K_LEFT:
					accelx = True
					dirX = -1
				if event.key == K_RIGHT:
					accelx = True
					dirX = 1
				if event.key == K_UP:
					accely = True
					dirY = -1
				if event.key == K_DOWN:
					accely = True
					dirY = 1
				if event.key == K_SPACE:
					trigger = True

			if event.type == KEYUP:
				if event.key == ord('z'):
					reverseCheat = False
					#score = 0
				if event.key == ord('x'):
					slowCheat = False
					#score = 0
				if event.key == K_ESCAPE:
						terminate()

				if event.key == K_LEFT or event.key == K_RIGHT:
					accelx = False
					dirX = 0
				if event.key == K_UP or event.key == K_DOWN:
					accely = False
					dirY = 0
				if event.key == K_SPACE:
					trigger = False
					
				if event.key == K_F2:
					# Take screenshots!
					pygame.image.save(windowSurface, ('image%s.jpg' % (endName)))
					endName += 1

				if event.key == K_F3:
					# Toggle debugging mode
					debug = not debug

		# Add new baddies at the top of the screen, if needed.
		baddieAddCounter += 1
		if baddieAddCounter == addNewBaddieRate and len(baddies) < MAXBADDIES:
			baddieAddCounter = 0
			newBaddie = {'rect': pygame.Rect(random.randint(0, WINDOWWIDTH-BADDIESIZE), 0 - BADDIESIZE, BADDIECOLLISION, BADDIECOLLISION),
						'speed': random.randint(BADDIEMINSPEED, BADDIEMAXSPEED),
						'surface':pygame.transform.scale(baddieImage, (BADDIESIZE, BADDIESIZE)),
						}

			baddies.append(newBaddie)
		
		# Delete backgrounds that have move past the screen
		for b in backgroundList[:]:
			if b.top == WINDOWHEIGHT:
				backgroundList.remove(b)	
		
		# Add to background list if needed and align backgrounds
		if len(backgroundList) < 2:
			for b in range(abs(len(backgroundList) - 2)):
				backgroundList.append(copy.deepcopy(backgroundRect))
		backgroundList[0].bottom = backgroundList[1].top

		# Move the player around.
		if accelx:
			if playerSpeedX != MAXSPEED and playerSpeedX != -MAXSPEED:
				playerSpeedX += PLAYERACCEL * dirX
		if accely:
			if playerSpeedY != MAXSPEED and playerSpeedY != -MAXSPEED:
				playerSpeedY += PLAYERACCEL * dirY
				
		# Here's where we deaccelerate the player
		if not accelx:
			if playerSpeedX > 0:
				playerSpeedX -= PLAYERDEACCEL
				# Gotta make sure we don't get stuck in a addition-subtraction
				# loop if the speed goes higher/lower than 0.
				if playerSpeedX < 0:
					playerSpeedX = 0
			if playerSpeedX < 0:
				playerSpeedX += PLAYERDEACCEL
				if playerSpeedX > 0:
					playerSpeedX = 0
		if not accely:
			if playerSpeedY > 0:
				playerSpeedY -= PLAYERDEACCEL
				if playerSpeedY < 0:
					playerSpeedY = 0
			if playerSpeedY < 0:
				playerSpeedY += PLAYERDEACCEL
				if playerSpeedY > 0:
					playerSpeedY = 0
		
		playerRect.left += playerSpeedX
		# Not the most elegant way to stop the player from leaving the screen
		# but like I said, it works.
		if playerRect.left < 0:
			playerRect.left = 0
			playerSpeedX = 0
		if playerRect.right > WINDOWWIDTH:
			playerRect.right = WINDOWWIDTH
			playerSpeedX = 0

		playerRect.top += playerSpeedY
		if playerRect.bottom > WINDOWHEIGHT:
			playerRect.bottom = WINDOWHEIGHT
			playerSpeedY = 0
		if playerRect.top < 0:
			playerRect.top = 0
			playerSpeedY = 0
			
		# Add bullets while shoot button is held down
		if trigger and len(bullets) < MAXBULLETS:
			bulletCounter += 1
			if bulletCounter == BULLETRATE:
				laserSound.play()
				bullets.append(pygame.Rect(playerRect.centerx, playerRect.top, 6, 20))
			if bulletCounter > BULLETRATE:
				bulletCounter = 0
		if not trigger:
			bulletCounter = BULLETRATE - 1
		
		# Move Background
		for b in backgroundList:
			b.move_ip(0, BACKGROUNDSCROLLRATE)

		# Move the baddies down.
		for b in baddies:
			if not reverseCheat and not slowCheat:
				b['rect'].move_ip(0, b['speed'])
			elif reverseCheat:
				b['rect'].move_ip(0, -5)
			elif slowCheat:
				b['rect'].move_ip(0, 1)
		
		# Move bullets up.
		for b in bullets:
			b.move_ip(0, -1 * BULLETSPEED)
			
		# Delete baddies and bullets that collide, add to score, update baddie rate if needed
		for a in baddies:
			for b in bullets[:]:
				if b.colliderect(a['rect']):
					killedBaddies.append({'rect':copy.deepcopy(a['rect']), 'frame':1, 'count':0})
					bullets.remove(b)
					baddies.remove(a)
					score += 100
					kills += 1
					if kills == toNextLevel and addNewBaddieRate > DIFFICULTY[1]:
						baddieAddCounter = 0
						addNewBaddieRate -= DIFFICULTY[1]
						toNextLevel *= 2
					explosionSound.play()
		
		# Delete baddies that have fallen past the bottom.
		for b in baddies[:]:
			if b['rect'].top > WINDOWHEIGHT:
				baddies.remove(b)

		# Delete bullets that have flown past the top.
		for b in bullets[:]:
			if b.bottom < -BADDIESIZE:
				bullets.remove(b)
		
		# Draw the game world on the window.
		#windowSurface.fill(BACKGROUNDCOLOR)
		
		#Draw background
		for b in range(len(backgroundList)):
			windowSurface.blit(backgroundScaled, backgroundList[b])
			# I used this when the background started derping around
			if debug:
				pygame.draw.line(windowSurface, (255, 255, 255), backgroundList[b].topleft, backgroundList[b].topright)
				pygame.draw.line(windowSurface, (255, 255, 255), backgroundList[b].bottomleft, backgroundList[b].bottomright)
				pygame.draw.line(windowSurface, (255, 255, 255), backgroundList[b].topleft, backgroundList[b].bottomright)
				pygame.draw.line(windowSurface, (255, 255, 255), backgroundList[b].bottomleft, backgroundList[b].topright)
		
		# Draw explosions of killed baddies
		for k in killedBaddies[:]:
			if k['frame'] == 1:
				windowSurface.blit(explosionFrame1Scaled, k['rect'])
				drawText('100', font, EXPLOSIONTEXTCOLOR, windowSurface, k['rect'].left, (k['rect'].top - 10))
				k['count'] += 1
				if k['count'] == 5:
					k['frame'] += 1
					k['count'] = 0
			if k['frame'] == 2:
				windowSurface.blit(explosionFrame2Scaled, k['rect'])
				drawText('100', font, EXPLOSIONTEXTCOLOR, windowSurface, k['rect'].left, (k['rect'].top - 30))
				k['count'] += 1
				if k['count'] == 5:
					k['frame'] += 1
					k['count'] = 0
			if k['frame'] == 3:
				drawText('100', font, EXPLOSIONTEXTCOLOR, windowSurface, k['rect'].left, (k['rect'].top - 50))
				k['count'] += 1
				if k['count'] == 5:	
					killedBaddies.remove(k)

		# Draw the player's rectangle
		windowSurface.blit(playerImage, (playerRect.left - (playerRect.width / 2) , playerRect.top - (playerRect.height / 2)))
		if debug:
			pygame.draw.rect(windowSurface, (0, 0, 255), playerRect)

		# Draw each baddie
		for b in baddies:
			windowSurface.blit(b['surface'], (b['rect'].left - (b['rect'].width / 2), b['rect'].top - (b['rect'].height / 2)))
			if debug:
				pygame.draw.rect(windowSurface, (255, 0, 0), b['rect'])
		
		# Draw each bullet
		for b in bullets:
			windowSurface.blit(laserImage, b)
			
		# Draw the score and top score.
		drawText('Score: %s' % (score), font, TEXTCOLOR, windowSurface, 10, 0)
		drawText('Kills: %s' % (kills), font, TEXTCOLOR, windowSurface, 10, 35)
		drawText('Top Score: %s' % (topScore), font, TEXTCOLOR, windowSurface, 10, 70)
		if debug:
			# Shows extra debugging line under the score, change shown variables as needed
			drawText('%r %r %r %r %r' % (toNextLevel, addNewBaddieRate, baddieAddCounter, len(baddies), len(bullets)), font, EXPLOSIONTEXTCOLOR, windowSurface, 10, 105)

		pygame.display.update()

		# Check if any of the baddies have hit the player.
		if playerHasHitBaddie(playerRect, baddies):
			if score > topScore:
				topScore = score # set new top score
			break

		mainClock.tick(FPS)

	# Stop the game and show the "Game Over" screen.
	pygame.mixer.music.stop()
	gameOverSound.play()
	pygame.time.wait(3000)
	windowSurface.fill(BACKGROUNDCOLOR)
	windowSurface.blit(explosionFrame1, playerRect)
	pygame.display.update()
	pygame.time.wait(500)
	windowSurface.fill(BACKGROUNDCOLOR)
	windowSurface.blit(explosionFrame2, playerRect)
	pygame.display.update()
	pygame.time.wait(500)
	
	windowSurface.fill(BACKGROUNDCOLOR)
	drawText('GAME OVER', font, TEXTCOLOR, windowSurface, (WINDOWWIDTH / 3), (WINDOWHEIGHT / 3))
	drawText('Press a key to play again.', font, TEXTCOLOR, windowSurface, (WINDOWWIDTH / 3) - 80, (WINDOWHEIGHT / 3) + 50)
	pygame.display.update()
	pygame.event.get()
	waitForPlayerToPressKey()

	gameOverSound.stop()
