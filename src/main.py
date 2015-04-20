# Cosplay Chase
# A top-down stealth game

import argparse
import cProfile
import os

import pygame
from pygame.locals import *

import character
import world

ONEONSQRT2 = 0.70710678118

def main(screenRes):
    # Initialise screen
    pygame.init()
    screen = pygame.display.set_mode(screenRes, pygame.FULLSCREEN|pygame.DOUBLEBUF)
    pygame.display.set_caption('Cosplay Chase')
    screenRect = screen.get_rect()

    # Fill background
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((50,50,50))

    # Load level from tiled level file
    level = world.Level(os.path.join("data","world","test.tmx"))

    spawnLoc = level.data.get_object_by_name("Player")

    while True:
        level.dx = 0
        level.dy = 0
        sprites = pygame.sprite.Group()
        player = character.Player(spawnLoc.x, spawnLoc.y, 800, level)
        sprites.add(player)
        guards = character.GuardManager(player, level, screenRect)

        # Initialise clock
        clock = pygame.time.Clock()

        time = 0.0
        frames = 0
        start_time = pygame.time.get_ticks()

        while not guards.iscaptured(player):
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
            level.update(dt, dx, dy)
            sprites.update(dt, dx, dy)
            guards.update(dt, dx, dy)

            # Blit everything to the screen
            screen.blit(background, (0,0))
            level.draw(screenRect, screen)
            guards.draw(screen)
            sprites.draw(screen)
            pygame.display.flip()

        print("You've been caught and your weapon has been confiscated!")
        print("You lasted {:.1f} seconds.".format((pygame.time.get_ticks() - start_time) / 1000.0))

def resolution(raw):
    a = raw.split("x")
    if len(a) != 2:
        raise ValueError()
    return (int(a[0]), int(a[1]))
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A top-down stealth game.')
    parser.add_argument('--profile-file', action='store',
                        help="File to store profiling output in")
    parser.add_argument('-p', '--profile', action='store_true',
                        help="Enable profiling using cProfile")
    parser.add_argument('-r', '--resolution', action='store', type=resolution, default=(0,0),
                        help="Target screen resolution (e.g. 1920x1080)")
    args = parser.parse_args()
    if args.profile:
        cProfile.run("main(args.resolution)", filename=args.profile_file)
    else:
        main(args.resolution)
