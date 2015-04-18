# Cosplay Chase
# A top-down stealth game

import os

import pygame
from pygame.locals import *

import world
import character

ONEONSQRT2 = 0.70710678118

def main():
    # Initialise screen
    pygame.init()
    screen = pygame.display.set_mode((800,600))
    pygame.display.set_caption('Cosplay Chase')
    screenRect = screen.get_rect()

    sprites = pygame.sprite.Group()
    
    # Fill background
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((0,0,0))

    # Load level from tiled level file
    level = world.Level(os.path.join("data","world","test.tmx"))

    player = character.Player(80, 80, 512, level)
    sprites.add(player)
    
    # Initialise clock
    clock = pygame.time.Clock()

    time = 0.0
    frames = 0

    while 1:
        dt = clock.tick(200) / 1000.0
        time += dt
        frames += 1
        if time >= 1.0:
            fps = frames / time
            if fps < 70:
                print("WARNING: Low framerate: "+str(fps)+" FPS")
            time = 0.0
            frames = 0

        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return

        movedir = [0, 0]
        
        pressed = pygame.key.get_pressed()
        if pressed[K_LEFT]:
            movedir[0] -= 1
        if pressed[K_RIGHT]:
            movedir[0] += 1
        if pressed[K_UP]:
            movedir[1] -= 1
        if pressed[K_DOWN]:
            movedir[1] += 1

        if abs(movedir[0]) + abs(movedir[1]) == 2:
            movedir[0] *= ONEONSQRT2
            movedir[1] *= ONEONSQRT2
        player.move(movedir, dt)

        dx = player.rect.center[0] - screenRect.width / 2
        dy = player.rect.center[1] - screenRect.height / 2
        screenRect.left += dx
        screenRect.top += dy
        sprites.update(dt, dx, dy)
        
        # Blit everything to the screen
        screen.blit(background, (0,0))
        level.draw(screenRect, screen)
        sprites.draw(screen)
        pygame.display.flip()

if __name__ == '__main__': main()
