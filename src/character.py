import itertools
import math

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
        x1 += dx * dt
        x2 += dx * dt
        y1 += dy * dt
        y2 += dy * dt
        t -= dt
        yield x1, y1, x2, y2, t*dx, t*dy
        dt = 1.0
        if dx > 0:
            dt = min(dt, (math.floor(x1) + 1 - x1) / dx)
        elif dx < 0:
            dt = min(dt, (x1 - 1 - math.ceil(x1)) / dx)
        if dy > 0:
            dt = min(dt, (math.floor(y1) + 1 - y1) / dy)
        elif dy < 0:
            dt = min(dt, (y1 - 1 - math.ceil(y1)) / dy)
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
        
        self.set_pos((current[0] + dx, current[1] + dy))

        # for x1, y1, x2, y2, dxr, dyr in walk(self.rect.left, self.rect.top, self.rect.right, self.rect.bottom, dx, dy):
        #     y = math.floor(y1) if y1 > y2 else math.ceil(y1) - 1
        #     collidey = False
        #     for x in xrange(int(math.floor(min(x1, x2))), int(math.ceil(max(x1,x2)))):
        #         if not self.level.passable((x,y)):
        #             collidey = True
        #             break
        #     x = math.floor(x1) if x1 > x2 else math.ceil(x1) - 1
        #     collidex = False
        #     for y in xrange(int(math.floor(min(y1, y2))), int(math.ceil(max(y1,y2)))):
        #         if not self.level.passable((x,y)):
        #             collidex = True
        #             break
        #     if collidey:
        #         self.set_pos((current[0] + dx - dxr, current[1] + dy - dyr))
        #         return
        #         # if collidex:
        #         #     self.set_pos((current[0] + dx - dxr, current[1] + dy - dyr))
        #         #     return
        #         # else:
        #         #     sign_x = 1 if dx > 0 else -1
        #         #     for xp in xrange(x+sign_x, math.ceil(x1+dxr) - 1 if x1 > x2 else math.floor(x1+dxr), sign_x):
        #         #         for y in xrange(math.floor(min(y1, y2)), math.ceil(max(y1,y2))):
        #         #             if not self.level.passable((x,y)):
        #         #                 self.set_pos((current[0] + dx - dxr, current[1] + dy - dyr))
        #         #                 return
        #     else:
        #         if collidex:
        #             self.set_pos((current[0] + dx - dxr, current[1] + dy - dyr))
        #             return
        #         else:
        #             continue

    def set_pos(self, pos):
        self.pos = pos
        self.rect.center = pos

    def update(self, dt, dx, dy):
        self.set_pos((self.pos[0] - dx, self.pos[1] - dy))

    def intersecting_tiles(self):
        tw = self.level.data.tilewidth
        th = self.level.data.tileheight
        left = math.floor(self.rect.left / tw)
        right = math.floor(self.rect.right / tw)
        top = math.floor(self.rect.top / th)
        bottom = math.floor(self.rect.bottom / th)
        return product(range(left, right), range(top, bottom))

    def top_tiles(self):
        tw = self.level.data.tilewidth
        th = self.level.data.tileheight
        left = math.floor(self.rect.left / tw)
        right = math.floor(self.rect.right / tw)
        top = math.floor(self.rect.top / th)
        return ((x,top) for x in range(left, right))

    def bottom_tiles(self):
        tw = self.level.data.tilewidth
        th = self.level.data.tileheight
        left = math.floor(self.rect.left / tw)
        right = math.floor(self.rect.right / tw)
        bottom = math.floor(self.rect.bottom / th)
        return ((x,bottom) for x in range(left, right))

    def left_tiles(self):
        tw = self.level.data.tilewidth
        th = self.level.data.tileheight
        left = math.floor(self.rect.left / tw)
        top = math.floor(self.rect.top / th)
        bottom = math.floor(self.rect.bottom / th)
        return ((left,y) for y in range(top, bottom))

    def right_tiles(self):
        tw = self.level.data.tilewidth
        th = self.level.data.tileheight
        right = math.floor(self.rect.right / tw)
        top = math.floor(self.rect.top / th)
        bottom = math.floor(self.rect.bottom / th)
        return ((right,y) for y in range(top, bottom))
    
class Player(Character):
    """Player character"""

    def __init__(self, x, y, speed, level):
        surf = pygame.Surface((64, 64))
        surf.fill((100, 100, 100))
        Character.__init__(self, surf, x, y, speed, level)
