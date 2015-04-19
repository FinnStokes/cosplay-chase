import itertools
import math
import time

import pygame
from pygame.locals import *

def walk(left, top, right, bottom, dx, dy):
    t = 1.0
    dt = 0.0
    x1 = left if dx < 0 else right
    x2 = right if dx < 0 else left
    y1 = top if dy < 0 else bottom
    y2 = bottom if dy < 0 else top
    while dt <= t:
        # print(dt, x1 + 1 - math.ceil(x1), dx)
        # print(dt, y1 + 1 - math.ceil(y1), dy)
        x1 += dx * dt
        x2 += dx * dt
        y1 += dy * dt
        y2 += dy * dt
        t -= dt
        yield x1, y1, x2, y2, t*dx, t*dy
        dt = 1.0
        if dx > 0:
            dt = min(dt, (math.floor(x1) + 1 - x1) * 1.0 / dx)
        elif dx < 0:
            dt = min(dt, (math.ceil(x1) - 1 - x1) * 1.0 / dx)
        if dy > 0:
            dt = min(dt, (math.floor(y1) + 1 - y1) * 1.0 / dy)
        elif dy < 0:
            dt = min(dt, (math.ceil(y1) - 1 - y1) * 1.0 / dy)
        if dt == 0.0:
            break


class Character(pygame.sprite.Sprite):
    """A character that moves around the level."""

    def __init__(self, image, x, y, speed, level):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.pos = (x, y)
        self.rect = image.get_rect()
        self.rect.center = self.pos
        self.speed = speed
        self.level = level

    def move(self, direction, dt):
        current = self.pos

        dx = direction[0]*self.speed*dt
        dy = direction[1]*self.speed*dt

        tw = self.level.data.tilewidth
        th = self.level.data.tileheight

        left = self.rect.left + self.level.dx
        right = self.rect.right + self.level.dx
        top = self.rect.top + self.level.dy
        bottom = self.rect.bottom + self.level.dy

        # print("-------------")
        # print(dx, dy)
        for x1, y1, x2, y2, dxr, dyr in walk(left * 1.0 / tw, top * 1.0 / th, right * 1.0 / tw, bottom * 1.0 / th, dx * 1.0 / tw, dy * 1.0 / th):
            # print("-------------")
            # print(x1, y1, x2, y2)
            # print(dxr, dyr)
            # print("y")
            y = int(math.floor(y1) if y1 > y2 else math.ceil(y1) - 1)
            collidey = False
            for xp in xrange(int(math.floor(min(x1, x2))), int(math.ceil(max(x1,x2)))):
                # print(xp, y, self.level.passable((xp,y)))
                if not self.level.passable((xp,y)):
                    collidey = True
                    break
            # print("x")
            x = int(math.floor(x1) if x1 > x2 else math.ceil(x1) - 1)
            collidex = False
            for yp in xrange(int(math.floor(min(y1, y2))), int(math.ceil(max(y1,y2)))):
                # print(x, yp, self.level.passable((x,yp)))
                if not self.level.passable((x,yp)):
                    collidex = True
                    break
            # print(collidex, collidey)
            if collidey:
                if collidex:
                    self.set_pos((current[0] + dx - dxr*tw, current[1] + dy - dyr*th))
                    return
                else:
                    sign_x = 1 if dx > 0 else -1
                    for xp in xrange(int(x+sign_x), int(math.ceil(x1+dxr) if x1 > x2 else (math.floor(x1+dxr) - 1)), sign_x):
                        for y in xrange(int(math.floor(min(y1, y2))), int(math.ceil(max(y1,y2)))):
                            if not self.level.passable((xp,y)):
                                if dx > 0:
                                    dxr = max(0.0, dxr - (xp - x) - (math.ceil(x1) - 1 - x1))
                                else:
                                    dxr = min(0.0, dxr - (xp - x) - (math.floor(x1) + 1 - x1))
                                self.set_pos((current[0] + dx - dxr*tw, current[1] + dy - dyr*th))
                                return
                    self.set_pos((current[0] + dx, current[1] + dy - dyr*th))
                    return
            else:
                if collidex:
                    # print("justx")
                    sign_y = 1 if dy > 0 else -1
                    for yp in xrange(int(y+sign_y), int(math.ceil(y1+dyr) if y1 > y2 else (math.floor(y1+dyr) - 1)), sign_y):
                        for x in xrange(int(math.floor(min(x1, x2))), int(math.ceil(max(x1,x2)))):
                            if not self.level.passable((x,yp)):
                                if dy > 0:
                                    dyr = max(0.0, dyr - (yp - y) - (math.ceil(y1) - 1 - y1))
                                else:
                                    dyr = min(0.0, dyr - (yp - y) - (math.floor(y1) + 1 - y1))
                                # print("!", dx - dxr*tw, dy)
                                self.set_pos((current[0] + dx - dxr*tw, current[1] + dy - dyr*th))
                                return
                    # print(dx - dxr*tw, dy)
                    self.set_pos((current[0] + dx - dxr*tw, current[1] + dy))
                    return
                else:
                    if dx != 0.0 and dy != 0.0 and not self.level.passable((x,y)):
                        self.set_pos((current[0] + dx - dxr*tw, current[1] + dy - dyr*th))
                        return
                    else:
                        continue

        self.set_pos((current[0] + dx, current[1] + dy))

    def set_pos(self, pos):
        self.pos = pos
        self.rect.center = pos

    def update(self, dt, dx, dy):
        self.set_pos((self.pos[0] - dx, self.pos[1] - dy))
    
class Player(Character):
    """Player character"""

    def __init__(self, x, y, speed, level):
        surf = pygame.Surface((60, 60))
        surf.fill((100, 100, 100))
        Character.__init__(self, surf, x, y, speed, level)
