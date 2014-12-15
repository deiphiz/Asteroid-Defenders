import pygame, random, sys, copy
from pygame.locals import *

WINDOWWIDTH = 800
WINDOWHEIGHT = 600
FPS = 30
TEXTCOLOR = (100, 255, 100)
EXPLOSIONTEXTCOLOR = (255, 255, 255)
BACKGROUNDCOLOR = (0, 0, 0)
HPWIDTH = 200
BULLETSPEED = 20 # I wouldn't set this any higher than BADDIECOLLISION
BULLETRATE = 8 # Setting this too low causes the program to crash when firing large barrages of bullets. Not sure why yet.
MAXBULLETS = 20
BADDIESIZE = 90
BADDIECOLLISION = 60 # Remember that setting this lower will reduce stupid player collision, but will also make baddies harder to hit
PLAYERCOLLISION = 45 # Also don't set these higher than the size of the player/baddies or the collision box will be OUTSIDE the sprite
INVINCIBLETIME = 60
EXPLOSIONSIZE = 48
BADDIEMINSPEED = 4
BADDIEMAXSPEED = 6
MAXBADDIES = 15
PLAYERHEALTH = 5
BASEHEALTH = 20
PLAYERMOVERATE = 14
BACKGROUNDSCROLLRATE = 1
DIFFICULTY = (30, 3, 5) #First is initial rate of spawn, second is how much is subtracted when moving to next level, last is lowest rate
SCORERATE = 15

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
pygame.display.set_caption('Asteroid Defender')
pygame.mouse.set_visible(False)

# set up fonts
font = pygame.font.SysFont("OCR A Extended", 24)
titleFont = pygame.font.SysFont("OCR A Extended", 32)
hudFont = pygame.font.SysFont("OCR A Extended", 18)

# set up sounds
gameOverSound = pygame.mixer.Sound('data\\gameover.wav')
gameOverSound.set_volume(0.2)
laserSound = pygame.mixer.Sound('data\\laser.wav')
laserSound.set_volume(0.1)
explosionSound = pygame.mixer.Sound('data\\explosion.wav')
explosionSound.set_volume(0.075)
hurtSound = pygame.mixer.Sound('data\\hurt.wav')
hurtSound.set_volume(0.2)
baseHurtSound = pygame.mixer.Sound('data\\basehurt.wav')
baseHurtSound.set_volume(0.2)
pygame.mixer.music.load('data\\music2.ogg')
pygame.mixer.music.set_volume(0.2)

# set up images
playerImage = pygame.image.load('data\\player.png')
playerHurtImage = pygame.image.load('data\\playerhurt.png')
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
baseImage = pygame.image.load('data\\spacestation.png')
baseScaled = pygame.transform.scale(baseImage, (WINDOWWIDTH, WINDOWWIDTH))
baseHurtImage = pygame.image.load('data\\spacestationhurt.png')
baseHurtScaled = pygame.transform.scale(baseHurtImage, (WINDOWWIDTH, WINDOWWIDTH))

# show the "Start" screen
windowSurface.blit(backgroundScaled, (0, 0))
drawText('--ASTEROID DEFENDER--', titleFont, TEXTCOLOR, windowSurface, 20, (WINDOWHEIGHT / 3))
drawText('Defend your base from the asteroids!', font, TEXTCOLOR, windowSurface, 20, (WINDOWHEIGHT / 3) + 40)
drawText('Use the arrow keys to move,', font, TEXTCOLOR, windowSurface, 20, (WINDOWHEIGHT / 3) + 80)
drawText('Press the spacebar to shoot! ', font, TEXTCOLOR, windowSurface, 20, (WINDOWHEIGHT / 3) + 120)
drawText('Press any key to start...', font, TEXTCOLOR, windowSurface, 20, (WINDOWHEIGHT / 3) + 160)
pygame.display.update()
waitForPlayerToPressKey()

#set up high score
with open('highscore', 'w+') as f:
	f.seek(0)
	if f.read() == '':
		f.write('10000')
	f.seek(0)
	highScore = int(f.read())

while True:
	# set up the start of the game
	baddies = []
	bullets = []
	backgroundList = []
	killedBaddies = []
	trigger = False
	score = 0
	scoreCounter = 0
	kills = 0
	baddiesCrossed = 0
	toNextLevel = 20
	playerRect.topleft = (WINDOWWIDTH / 2, WINDOWHEIGHT - 50)
	playerHealth = PLAYERHEALTH
	baseHealth = BASEHEALTH
	hurt = False
	baseHurt = False
	invincible = False
	invincibleTime = INVINCIBLETIME
	moveLeft = moveRight = moveUp = moveDown = False
	reverseCheat = slowCheat = False
	baddieAddCounter = 0
	addNewBaddieRate = DIFFICULTY[0]
	bulletCounter = BULLETRATE - 1
	pygame.mixer.music.play(-1, 0.0)
	endName = 1
	debug = False

	while True: # the game loop runs while the game part is playing
	
		#increase score
		scoreCounter += 1
		if scoreCounter >= SCORERATE:
			score += 5
			scoreCounter = 0
		
		#set high score
		if score >= highScore:
			highScore = score

		for event in pygame.event.get():
			if event.type == QUIT:
				terminate()

			if event.type == KEYDOWN:
				if event.key == ord('z'):
					reverseCheat = True
				if event.key == ord('x'):
					slowCheat = True
				if event.key == K_LEFT or event.key == ord('a'):
					moveRight = False
					moveLeft = True
				if event.key == K_RIGHT or event.key == ord('d'):
					moveLeft = False
					moveRight = True
				if event.key == K_UP or event.key == ord('w'):
					moveDown = False
					moveUp = True
				if event.key == K_DOWN or event.key == ord('s'):
					moveUp = False
					moveDown = True
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

				if event.key == K_LEFT or event.key == ord('a'):
					moveLeft = False
				if event.key == K_RIGHT or event.key == ord('d'):
					moveRight = False
				if event.key == K_UP or event.key == ord('w'):
					moveUp = False
				if event.key == K_DOWN or event.key == ord('s'):
					moveDown = False
				if event.key == K_SPACE:
					trigger = False
					
				if event.key == K_F2:
					# Take screenshots!
					pygame.image.save(windowSurface, ('image%s.jpg' % (endName)))
					endName += 1

				if event.key == K_F3:
					# Toggle debugging mode
					debug = not debug

			if event.type == MOUSEMOTION:
				# If the mouse moves, move the player where the cursor is.
				playerRect.move_ip(event.pos[0] - playerRect.centerx, event.pos[1] - playerRect.centery)
			
			if event.type == MOUSEBUTTONDOWN:
				trigger = True
			if event.type == MOUSEBUTTONUP:
				trigger = False
		
		# Add new baddies at the top of the screen, if needed.
		baddieAddCounter += 1
		if baddieAddCounter >= addNewBaddieRate and len(baddies) < MAXBADDIES:
			baddieAddCounter = 0
			newBaddie = {'rect': pygame.Rect(random.randint(0, WINDOWWIDTH-BADDIESIZE), 0 - BADDIESIZE, BADDIECOLLISION, BADDIECOLLISION),
						'speed': random.randint(BADDIEMINSPEED, BADDIEMAXSPEED),
						'angle': random.randint(-5,5),
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
		if moveLeft and playerRect.left > 0:
			playerRect.move_ip(-1 * PLAYERMOVERATE, 0)
		if moveRight and playerRect.right < WINDOWWIDTH:
			playerRect.move_ip(PLAYERMOVERATE, 0)
		if moveUp and playerRect.top > 0:
			playerRect.move_ip(0, -1 * PLAYERMOVERATE)
		if moveDown and playerRect.bottom < WINDOWHEIGHT:
			playerRect.move_ip(0, PLAYERMOVERATE)
			
		# Add bullets while mouse button is held down
		if trigger and len(bullets) < MAXBULLETS:
			bulletCounter += 1
			if bulletCounter == BULLETRATE:
				laserSound.play()
				bullets.append(pygame.Rect(playerRect.centerx, playerRect.top, 6, 20))
			if bulletCounter > BULLETRATE:
				bulletCounter = 0
		if not trigger:
			bulletCounter = BULLETRATE - 1

		# Move the mouse cursor to match the player.
		pygame.mouse.set_pos(playerRect.centerx, playerRect.centery)
		
		# Move Background
		for b in backgroundList:
			b.move_ip(0, BACKGROUNDSCROLLRATE)

		# Move the baddies down.
		for b in baddies:
			if not reverseCheat and not slowCheat:
				b['rect'].move_ip(b['angle'], b['speed'])
				if (b['rect'].left < 0) or (b['rect'].right > WINDOWWIDTH):
					b['angle'] *= -1
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
					if kills == toNextLevel and addNewBaddieRate > DIFFICULTY[2]:
						baddieAddCounter = 0
						addNewBaddieRate -= DIFFICULTY[1]
						if addNewBaddieRate < DIFFICULTY[2]:
							addNewBaddieRate = DIFFICULTY[2]
						toNextLevel *= 2
					explosionSound.play()
		
		#Check if player hit baddie and lower health of player.
		if playerHasHitBaddie(playerRect, baddies) and not invincible:
			playerHealth -= 1
			hurt = True
			invincible = True
			
		#Lower invincible time if true.
		if invincible and invincibleTime > 0:
			invincibleTime -= 1
		elif invincibleTime <= 0:
			invincible = False
			invincibleTime = INVINCIBLETIME
		
		# Delete baddies that have fallen past the bottom and lower health of base.
		for b in baddies[:]:
			if b['rect'].top > WINDOWHEIGHT:
				baseHurt = True
				baseHealth -= 1
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
		
		#draw base
		if baseHurt:
			baseHurtSound.play()
			windowSurface.blit(baseHurtScaled, (0, WINDOWHEIGHT-WINDOWHEIGHT/2))
			baseHurt = False
		else:
			windowSurface.blit(baseScaled, (0, WINDOWHEIGHT-WINDOWHEIGHT/2))
		
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

		# Draw the player's image
		if not invincible or (invincible and invincibleTime%2 == 0):
			windowSurface.blit(playerImage, (playerRect.left - (playerRect.width / 2) , playerRect.top - (playerRect.height / 2)))
				
		if debug:
			pygame.draw.rect(windowSurface, (0, 0, 255), playerRect)

		# Draw each baddie
		for b in baddies:
			windowSurface.blit(b['surface'], (b['rect'].left - ((BADDIESIZE - BADDIECOLLISION) / 2), b['rect'].top - ((BADDIESIZE - BADDIECOLLISION) / 2)))
			if debug:
				pygame.draw.rect(windowSurface, (255, 0, 0), b['rect'])
		
		# Draw each bullet
		for b in bullets:
			windowSurface.blit(laserImage, b)
			
		# Draw the score and top score.
		drawText('Score: %s High: %s' % (score, highScore), hudFont, TEXTCOLOR, windowSurface, 10, 0)
		
		#Draw player HP Bar
		pygame.draw.rect(windowSurface, (255,0,0), (10,25, playerHealth*HPWIDTH/PLAYERHEALTH, 20))
		pygame.draw.rect(windowSurface, (128,128,128), (10,25, HPWIDTH, 20), 2)
		drawText('HP: %s/%s' % (playerHealth, PLAYERHEALTH), hudFont, (255,255,255), windowSurface, 15, 25)
		
		#Draw Base HP Bar
		pygame.draw.rect(windowSurface, (0,255,0), (10,50, baseHealth*HPWIDTH/BASEHEALTH, 20))
		pygame.draw.rect(windowSurface, (128,128,128), (10,50, HPWIDTH, 20), 2)
		drawText('HP: %s/%s' % (baseHealth, BASEHEALTH), hudFont, (255,255,255), windowSurface, 15, 50)
		
		#drawText('HP: %s Base HP: %s' % (playerHealth, baseHealth), font, TEXTCOLOR, windowSurface, 10, 35)
		#drawText('Kills: %s' % (kills), font, TEXTCOLOR, windowSurface, 10, 70)
		if debug:
			# Shows extra debugging line under the score, change shown variables as needed
			drawText('%r %r %r %r %r' % (toNextLevel, addNewBaddieRate, baddieAddCounter, len(baddies), len(bullets)), font, EXPLOSIONTEXTCOLOR, windowSurface, 10, 140)
		
		# Check if game state should be over
		if (playerHealth == 0) or (baseHealth == 0):
			with open('highscore', 'w+') as f:
				f.write(str(highScore))
			break		
		
		# Flash the screen if hurt
		if hurt:
			hurtSound.play()
			pygame.draw.rect(windowSurface, (255, 0, 0), (0, 0, WINDOWWIDTH, WINDOWHEIGHT))
			hurt = False

		pygame.display.update()
		mainClock.tick(FPS)

	# Stop the game and show the "Game Over" animation and screen.
	pygame.mixer.music.stop()
	windowSurface.fill((255,0,0))
	windowSurface.blit(playerHurtImage, (playerRect.left - (playerRect.width / 2) , playerRect.top - (playerRect.height / 2)))
	pygame.display.update()
	hurtSound.play()
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
