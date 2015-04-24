import heapq
import itertools
import math

import pygame
from pygame.locals import *
from pygame import gfxdraw

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
            dt = min(dt, float(math.floor(x1) + 1 - x1) / dx)
        elif dx < 0:
            dt = min(dt, float(math.ceil(x1) - 1 - x1) / dx)
        if dy > 0:
            dt = min(dt, float(math.floor(y1) + 1 - y1) / dy)
        elif dy < 0:
            dt = min(dt, float(math.ceil(y1) - 1 - y1) / dy)
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
        self.dx = 0
        self.dy = 0

    def move(self, direction, dt):
        current = self.pos

        dx = direction[0]*self.speed*dt
        dy = direction[1]*self.speed*dt

        tw = self.level.data.tilewidth
        th = self.level.data.tileheight

        left = self.rect.left + self.dx
        right = self.rect.right + self.dx
        top = self.rect.top + self.dy
        bottom = self.rect.bottom + self.dy

        # print("-------------")
        # print(dx, dy)
        for x1, y1, x2, y2, dxr, dyr in walk(float(left) / tw, float(top) / th, float(right) / tw, float(bottom) / th, float(dx) / tw, float(dy) / th):
            # print("-------------")
            # print(x1, y1, x2, y2)
            # print(dxr, dyr)
            # print("y")
            y = int(math.floor(y1) if y1 > y2 else math.ceil(y1) - 1)
            collidey = False
            for xp in xrange(int(math.floor(min(x1, x2))), int(math.ceil(max(x1,x2)))):
                # print(xp, y, self.level.passable[xp][y])
                if not self.level.passable[xp][y]:
                    collidey = True
                    break
            # print("x")
            x = int(math.floor(x1) if x1 > x2 else math.ceil(x1) - 1)
            collidex = False
            for yp in xrange(int(math.floor(min(y1, y2))), int(math.ceil(max(y1,y2)))):
                # print(x, yp, self.level.passable[x][yp])
                if not self.level.passable[x][yp]:
                    collidex = True
                    break
            # print(collidex, collidey)
            if collidey:
                if collidex:
                    self.set_pos((current[0] + dx - dxr*tw, current[1] + dy - dyr*th))
                    return False
                else:
                    sign_x = 1 if dx > 0 else -1
                    for xp in xrange(int(x+sign_x), int(math.ceil(x1+dxr) if x1 > x2 else (math.floor(x1+dxr) - 1)), sign_x):
                        for y in xrange(int(math.floor(min(y1, y2))), int(math.ceil(max(y1,y2)))):
                            if not self.level.passable[xp][y]:
                                if dx > 0:
                                    dxr = max(0.0, dxr - (xp - x) - (math.ceil(x1) - 1 - x1))
                                else:
                                    dxr = min(0.0, dxr - (xp - x) - (math.floor(x1) + 1 - x1))
                                self.set_pos((current[0] + dx - dxr*tw, current[1] + dy - dyr*th))
                                return dxr == 0.0
                    self.set_pos((current[0] + dx, current[1] + dy - dyr*th))
                    return True
            else:
                if collidex:
                    # print("justx")
                    sign_y = 1 if dy > 0 else -1
                    for yp in xrange(int(y+sign_y), int(math.ceil(y1+dyr) if y1 > y2 else (math.floor(y1+dyr) - 1)), sign_y):
                        for x in xrange(int(math.floor(min(x1, x2))), int(math.ceil(max(x1,x2)))):
                            if not self.level.passable[x][yp]:
                                if dy > 0:
                                    dyr = max(0.0, dyr - (yp - y) - (math.ceil(y1) - 1 - y1))
                                else:
                                    dyr = min(0.0, dyr - (yp - y) - (math.floor(y1) + 1 - y1))
                                # print("!", dx - dxr*tw, dy)
                                self.set_pos((current[0] + dx - dxr*tw, current[1] + dy - dyr*th))
                                return dyr == 0.0
                    # print(dx - dxr*tw, dy)
                    self.set_pos((current[0] + dx - dxr*tw, current[1] + dy))
                    return True
                else:
                    if dx != 0.0 and dy != 0.0 and not self.level.passable[x][y]:
                        self.set_pos((current[0] + dx - dxr*tw, current[1] + dy - dyr*th))
                        return True
                    else:
                        continue

        self.set_pos((current[0] + dx, current[1] + dy))
        return True

    def tiles(self): 
        tw = self.level.data.tilewidth
        th = self.level.data.tileheight

        left = int(math.floor(float(self.rect.left + self.dx) / tw))
        right = int(math.ceil(float(self.rect.right + self.dx) / tw))
        top = int(math.floor(float(self.rect.top + self.dy) / th))
        bottom = int(math.ceil(float(self.rect.bottom + self.dy) / th))

        return itertools.product(xrange(left, right), xrange(top, bottom))

    def adjacent_tiles(self): 
        tw = self.level.data.tilewidth
        th = self.level.data.tileheight

        left = int(math.floor(float(self.rect.left + self.dx) / tw))
        right = int(math.ceil(float(self.rect.right + self.dx) / tw))
        top = int(math.floor(float(self.rect.top + self.dy) / th))
        bottom = int(math.ceil(float(self.rect.bottom + self.dy) / th))

        return (itertools.product(xrange(left, right+1), xrange(top, bottom+1)),
                itertools.product((left-1,), xrange(top, bottom+1)),
                itertools.product((right+1,), xrange(top, bottom+1)),
                itertools.product(xrange(left, right+1), (top-1,)),
                itertools.product(xrange(left, right+1), (bottom+1,)),
                itertools.chain(itertools.product((left-1,), xrange(top, bottom)), itertools.product(xrange(left-1, right), (top-1,))),
                itertools.chain(itertools.product((right+1,), xrange(top, bottom)), itertools.product(xrange(left+1, right+2), (top-1,))),
                itertools.chain(itertools.product((right+1,), xrange(top+1, bottom+1)), itertools.product(xrange(left+1, right+2), (bottom+1,))),
                itertools.chain(itertools.product((left-1,), xrange(top+1, bottom+1)), itertools.product(xrange(left-1, right), (bottom+1,))),
        )

    def set_pos(self, pos):
        self.pos = pos
        self.rect.center = (pos[0] - self.dx, pos[1] - self.dy)

    def update(self, dt, dx, dy):
        self.dx += dx
        self.dy += dy
        self.set_pos(self.pos)

class Player(Character):
    """Player character"""

    def __init__(self, x, y, speed, level):
        surf = pygame.Surface((60, 60))
        surf.fill((100, 0, 0))
        Character.__init__(self, surf, x, y, speed, level)

class GuardManager:
    """Manages guards and their movement"""

    def __init__(self, player, level, screenRect):
        self.player = player
        self.level = level
        self.guards = pygame.sprite.Group()

        for o in level.data.objects:
            if o.type == "guard":
                guard = Guard(o.points, o.closed, 500, player, self, level, screenRect)
                self.guards.add(guard)

    def update(self, dt, dx, dy):
        self.guards.update(dt, dx, dy)

    def draw(self, surface):
        self.guards.draw(surface)
        for guard in self.guards:
            guard.draw(surface)

    def iscaptured(self, player):
        for guard in self.guards:
            if guard.rect.colliderect(player.rect):
                return True
        return False

FOV = math.pi/3
RANGE = 700

def normalise(angle):
    if angle > math.pi:
        return angle - 2*math.pi
    elif angle < -math.pi:
        return angle + 2*math.pi
    else:
        return angle

class Guard(Character):
    """Guard that moves towards player character"""

    def __init__(self, points, closed, speed, player, gm, level, screenRect):
        surf = pygame.Surface((40, 40))
        surf.fill((0, 0, 100))
        Character.__init__(self, surf, points[0][0], points[0][1], speed, level)
        self.player = player
        self.gm = gm
        self.facing = 0
        self.fov = FOV
        self.memory = {}
        self.polar = None
        self.points = points
        self.closed = closed
        self.currentpoint = 1
        self.pointdelta = 1
        self.sight = []
        self.viewbox = pygame.Rect(0, 0, 2*RANGE+2, 2*RANGE+2)
        self.screenRect = screenRect
        self.chosen = 0
        self.surface = None
        
    def update(self, dt, dx, dy):
        Character.update(self, dt, dx, dy)

        # Update memory
        if self.cansee(self.player):
            self.memory[self.player] = (self.player.pos[0], self.player.pos[1])
        # for guard in self.gm.guards:
        #     if self.cansee(guard):
        #         self.memory[guard] = (guard.pos[0], guard.pos[1])

        # Update movement
        direction = (0, 0)
        if self.player in self.memory:
            target = self.memory[self.player]
            if self.pos == target:
                del self.memory[self.player]
        else:
            target = self.points[self.currentpoint]
            if self.pos == target:
                self.next_point()
        direction = (target[0] - self.pos[0], target[1] - self.pos[1])
        mag = math.sqrt(direction[0]**2 + direction[1]**2)
        if mag < self.speed*dt:
            mag = self.speed*dt
        direction = (direction[0]/mag, direction[1]/mag)
        self.facing = math.atan2(-direction[1], direction[0])
        d = 1024
        for p in self.castray(self.facing, 0):
            if p[0][2]:
                d = p[0][1]
                break
        if d < 256:
            angle = (256 - d) * math.pi / 1024
            if self.chosen < 0:
                angle = min(angle * (1 - (self.chosen+1)/2.0), math.pi)
                d1 = 1024
                for p in self.castray(self.facing-angle, 0):
                    if p[0][2]:
                        d1 = p[0][1]
                        break
                if d1 < 256:
                    self.chosen -= dt
                else:
                    self.chosen = -1
                self.facing -= angle
            elif self.chosen > 0:
                angle = min(angle * (1 + (self.chosen-1)/2.0), math.pi)
                d2 = 1024
                for p in self.castray(self.facing+angle, 0):
                    if p[0][2]:
                        d2 = p[0][1]
                        break
                if d2 < 256:
                    self.chosen += dt
                else:
                    self.chosen = 1
                self.facing += angle
            else:
                d1 = 1024
                for p in self.castray(self.facing-angle, 0):
                    if p[0][2]:
                        d1 = p[0][1]
                        break
                d2 = 1024
                for p in self.castray(self.facing+angle, 0):
                    if p[0][2]:
                        d2 = p[0][1]
                        break
                if d1 > d2:
                    self.chosen = -1
                    self.facing -= angle
                else:
                    self.chosen = +1
                    self.facing += angle
            direction = (math.cos(self.facing), -math.sin(self.facing))
        else:
            if self.chosen > dt/2:
                self.chosen -= dt/2
            elif self.chosen < -dt/2:
                self.chosen += dt
            else:
                self.chosen = 0
        isstuck = not self.move(direction, dt)
        if isstuck:
            if self.player in self.memory:
                del self.memory[self.player]
            else:
                self.next_point()

        self.updateView()

    def updateView(self):
        left = 0
        right = 0
        top = 0
        bottom = 0

        start = normalise(self.facing - self.fov/2)
        end = normalise(self.facing + self.fov/2)
        if start < 0 or end < 0:
            bottom = RANGE
        if start > 0 or end > 0:
            top = -RANGE
        if (start < math.pi/2 and start > -math.pi/2) or (end < math.pi/2 and end > -math.pi/2):
            right = RANGE
        if start > math.pi/2 or start < -math.pi/2 or end > math.pi/2 or end < -math.pi/2:
            left = -RANGE
        self.viewbox = pygame.Rect(self.rect.center[0]+left-1, self.rect.center[1]+top-1, (right - left) + 2, (bottom - top) + 2)

        if self.viewbox.colliderect(self.screenRect):
            vertices = self.get_vertices()
            self.sight, self.polar = self.calc_view(vertices, -self.fov/2, self.fov/2)

    def calc_view(self, vertices, start, end):
        tw, th = self.level.data.tilewidth, self.level.data.tileheight

        sight = [(self.pos[0] - self.dx, self.pos[1] - self.dy)]
        polar = [(0, 0)]

        current = (-1, 0) # (orientation, position)
        hwalls = set()
        vwalls = set()

        old_dx = 0
        old_dy = 0

        for v in vertices:
            # print(current)
            angle = v[0]
            if angle > end:
                break
            tx, ty = v[2]
            dx = tx*tw - self.pos[0]
            dy = ty*tw - self.pos[1]
            if dx == 0 or old_dx*dx < 0:
                vwalls.clear()
                if current[0] == 0:
                    # find next nearest wall
                    if len(hwalls) == 0:
                        current = (-1, 0)
                    else:
                        ty = min(hwalls) if dy > 0 else max(hwalls)
                        current = (1, ty)
                        hwalls.remove(ty)                    
            if dy == 0 or old_dy*dy < 0:
                hwalls.clear()
                if current[0] == 1:
                    # find next nearest wall
                    if len(vwalls) == 0:
                        current = (-1, 0)
                    else:
                        tx = min(vwalls) if dx > 0 else max(vwalls)
                        current = (0, tx)
                        vwalls.remove(tx)                    
            old_dx = dx
            old_dy = dy
            if angle > start and len(polar) == 1:
                pos, dist = self.wall_intersection(current, start)
                # print("start", current, start, pos, dist)
                sight += [(pos[0] - self.dx, pos[1] - self.dy)]
                polar += [(start, dist)]
            # if vertex lies on current wall, terminate it
            if current[0] >= 0 and current[1] == v[2][current[0]]:
                # print("end wall", current)
                wall = current
                # add wall starting at v if it is in the right direction
                if dy*v[3][0] - dx*v[3][1] > 0:
                    if v[3][0] != 0 and v[3][1] == 0:
                        # print("h corner", v[2])
                        hwalls.add(v[2][1])
                    elif v[3][0] == 0 and v[3][1] != 0:
                        # print("v corner", v[2])
                        vwalls.add(v[2][0])
                # find next nearest wall
                if len(hwalls) == 0:
                    if len(vwalls) == 0:
                        current = (-1, 0)
                    else:
                        tx = min(vwalls) if dx > 0 else max(vwalls)
                        current = (0, tx)
                        vwalls.remove(tx)
                else:
                    if len(vwalls) == 0:
                        ty = min(hwalls) if dy > 0 else max(hwalls)
                        current = (1, ty)
                        hwalls.remove(ty)
                    else:
                        # set current to closest stored wall
                        tx = min(vwalls) if dx > 0 else max(vwalls)
                        ty = min(hwalls) if dy > 0 else max(hwalls)
                        # print(tx, ty)
                        if (tx*tw - self.pos[0])/dx < (ty*th - self.pos[1])/dy:
                            current = (0, tx)
                            vwalls.remove(tx)
                        else:
                            current = (1, ty)
                            hwalls.remove(ty)
                if angle > start:
                    old_dist = dx**2 + dy**2
                    new_cart, new_polar = self.interpolate_range(polar[-1], (angle, old_dist), wall, (v[2][0]*tw, v[2][1]*th))
                    if old_dist < RANGE**2:
                        pos, dist = self.wall_intersection(current, angle)
                        sight += new_cart + [(pos[0] - self.dx, pos[1] - self.dy)]
                        polar += new_polar + [(angle, dist)]
                    else:
                        sight += new_cart
                        polar += new_polar
            # otherwise, terminate intersecting walls
            else:
                if ty in hwalls:
                    # print("h endpoint", ty)
                    hwalls.remove(ty)
                if tx in vwalls:
                    # print("v endpoint", tx)
                    vwalls.remove(tx)
                # If wall is in right direction
                if dy*v[3][0] - dx*v[3][1] > 0:
                    # if vertex is closer than current, repace current with new wall
                    if current[0] < 0 or v[1] < self.wall_intersection(current, angle)[1]:
                        if angle > start:
                            pos, dist = self.wall_intersection(current, angle)
                            new_cart, new_polar = self.interpolate_range(polar[-1], (angle, dist), current, pos)
                            # print((pos[0]/tw, pos[1]/th), (tx, ty))
                            new_dist = dx**2 + dy**2
                            if new_dist <= RANGE**2:
                                sight += new_cart + [(tx*tw - self.dx, ty*th - self.dy)]
                                polar += new_polar + [(angle, new_dist)]
                            else:
                                if dist < RANGE**2:
                                    sight += new_cart + [(self.pos[0] + RANGE*math.cos(angle) - self.dx, ty*th - RANGE*math.sin(angle) - self.dy)]
                                    polar += new_polar + [(angle, RANGE**2)]
                                else:
                                    sight += new_cart
                                    polar += new_polar
                        if current[0] == 1:
                            hwalls.add(current[1])
                        elif current[0] == 0:
                            vwalls.add(current[1])
                        if v[3][0] != 0 and v[3][1] == 0:
                            # print("h in front", v[2])
                            current = (1, v[2][1])
                        elif v[3][0] == 0 and v[3][1] != 0:
                            # print("v in front", v[2])
                            current = (0, v[2][0])
                    # otherwise, store new wall
                    else:
                        if v[3][0] != 0 and v[3][1] == 0:
                            hwalls.add(v[2][1])
                            # print("h behind", v[2])
                        elif v[3][0] == 0 and v[3][1] != 0:
                            # print("v behind", v[2])
                            vwalls.add(v[2][0])

        if len(polar) <= 1:
            pos, dist = self.wall_intersection(current, start)
            sight += [(pos[0] - self.dx, pos[1] - self.dy)]
            polar += [(start, dist)]

        dx = RANGE*math.cos(end+self.facing)
        dy = -RANGE*math.sin(end+self.facing)
        if dx == 0 or old_dx*dx < 0:
            vwalls.clear()
            if current[0] == 0:
                # find next nearest wall
                if len(hwalls) == 0:
                    current = (-1, 0)
                else:
                    ty = min(hwalls) if dy > 0 else max(hwalls)
                    current = (1, ty)
                    hwalls.remove(ty)                    
        if dy == 0 or old_dy*dy < 0:
            hwalls.clear()
            if current[0] == 1:
                # find next nearest wall
                if len(vwalls) == 0:
                    current = (-1, 0)
                else:
                    tx = min(vwalls) if dx > 0 else max(vwalls)
                    current = (0, tx)
                    vwalls.remove(tx) 

        # print(current, hwalls, vwalls)
        pos, dist = self.wall_intersection(current, end)
        new_cart, new_polar = self.interpolate_range(polar[-1], (end, dist), current, pos)
        # print("end", current, start, pos, dist)
        sight += new_cart
        polar += new_polar

        # print(len(sight), len(polar))
        return sight, polar

    def interpolate_range(self, prev, current, wall, end):
        if wall[0] < 0:
            return self.arc(prev[0], current[0])
        else:
            if prev[1] < RANGE**2 and current[1] < RANGE**2:
                return [(end[0] - self.dx, end[1] - self.dy)], [current]
            else:
                tw, th = self.level.data.tilewidth, self.level.data.tileheight
                if wall[0] == 0:
                    dx = wall[1]*tw - self.pos[0]
                    if abs(dx) >= RANGE:
                        return self.arc(prev[0], current[0])
                    else:
                        dy = math.sqrt(RANGE**2 - dx**2)
                        if dx > 0:
                            if end[1] < self.pos[1] + dy:
                                a1 = normalise(math.atan2(-dy, dx) - self.facing)
                                if a1 > prev[0]:
                                    c1, p1 = self.arc(prev[0], a1)
                                else:
                                    c1, p1 = [], []
                                if end[1] < self.pos[1] - dy:
                                    a2 = normalise(math.atan2(dy, dx) - self.facing)
                                    if a2 <= prev[0]:
                                        return self.arc(prev[0], current[0])
                                    c2, p2 = self.arc(a2, current[0])
                                    return c1+[(wall[1]*tw - self.dx, self.pos[1] + dy - self.dy)]+c2, p1+[(a2, RANGE**2)]+p2
                                else:
                                    return c1+[(end[0] - self.dx, end[1] - self.dy)], p1+[current]
                            else:
                                return self.arc(prev[0], current[0])
                        else:
                            if end[1] > self.pos[1] - dy:
                                a1 = normalise(math.atan2(dy, dx) - self.facing)
                                if a1 > prev[0]:
                                    c1, p1 = self.arc(prev[0], a1)
                                else:
                                    c1, p1 = [], []
                                if end[1] > self.pos[1] + dy:
                                    a2 = normalise(math.atan2(-dy, dx) - self.facing)
                                    if a2 <= prev[0]:
                                        return self.arc(prev[0], current[0])
                                    c2, p2 = self.arc(a2, current[0])
                                    return c1+[(wall[1]*tw - self.dx, self.pos[1] + dy - self.dy)]+c2, p1+[(a2, RANGE**2)]+p2
                                else:
                                    return c1+[(end[0] - self.dx, end[1] - self.dy)], p1+[current]
                            else:
                                return self.arc(prev[0], current[0])
                else:
                    dy = wall[1]*th - self.pos[1]
                    # print(wall[1]*th, self.pos[1], dy)
                    if abs(dy) >= RANGE:
                        return self.arc(prev[0], current[0])
                    else:
                        dx = math.sqrt(RANGE**2 - dy**2)
                        if dy > 0:
                            # print("dy > 0")
                            # print(wall[1]*th, dx, dy)
                            # print(end[0], self.pos[0] + dx)
                            # print(prev[0], current[0])
                            if end[0] > self.pos[0] - dx:
                                a1 = normalise(math.atan2(-dy, -dx) - self.facing)
                                # print(a1)
                                if a1 > prev[0]:
                                    # print("arc in")
                                    c1, p1 = self.arc(prev[0], a1)
                                else:
                                    c1, p1 = [], []
                                if end[0] > self.pos[0] + dx:
                                    # print("arc out")
                                    a2 = normalise(math.atan2(-dy, dx) - self.facing)
                                    # print(a2)
                                    if a2 <= prev[0]:
                                        return self.arc(prev[0], current[0])
                                    c2, p2 = self.arc(a2, current[0])
                                    return c1+[(self.pos[0] + dx - self.dx, wall[1]*th - self.dy)]+c2, p1+[(a2, RANGE**2)]+p2
                                else:
                                    return c1+[(end[0] - self.dx, end[1] - self.dy)], p1+[current]
                            else:
                                return self.arc(prev[0], current[0])
                        else:
                            # print("dy < 0")
                            if end[0] < self.pos[0] + dx:
                                a1 = normalise(math.atan2(-dy, dx) - self.facing)
                                if a1 > prev[0]:
                                    c1, p1 = self.arc(prev[0], a1)
                                else:
                                    c1, p1 = [], []
                                if end[0] < self.pos[0] - dx:
                                    a2 = normalise(math.atan2(-dy, -dx) - self.facing)
                                    if a2 <= prev[0]:
                                        return self.arc(prev[0], current[0])
                                    c2, p2 = self.arc(a2, current[0])
                                    return c1+[(self.pos[0] - dx - self.dx, wall[1]*th - self.dy)]+c2, p1+[(a2, RANGE**2)]+p2
                                else:
                                    return c1+[(end[0] - self.dx, end[1] - self.dy)], p1+[current]
                            else:
                                return self.arc(prev[0], current[0])

    def arc(self, start, end):
        a = end - start
        n = max(int(20*a), 1)
        da = a / n
        return ([(self.pos[0] - self.dx + RANGE*math.cos(start + self.facing + da*i), self.pos[1] - self.dy - RANGE*math.sin(start + self.facing + da*i)) for i in xrange(1,n+1)],
                [(start + da*i, RANGE**2) for i in xrange(1,n+1)])
    
    def wall_intersection(self, wall, angle):
        angle += self.facing
        if wall[0] < 0:
            return (self.pos[0] + RANGE*math.cos(angle), self.pos[1] - RANGE*math.sin(angle)), RANGE**2
        elif wall[0] == 0:
            tw = self.level.data.tilewidth
            dx = wall[1]*tw - self.pos[0]
            r = (dx / math.cos(angle))**2
            if r <= RANGE**2:
                return (wall[1]*tw, self.pos[1] - dx * math.tan(angle)), r
            else:
                return (self.pos[0] + RANGE*math.cos(angle), self.pos[1] - RANGE*math.sin(angle)), RANGE**2
        else:
            th = self.level.data.tileheight
            dy = wall[1]*th - self.pos[1]
            c = math.cos(angle)
            s = math.sin(angle)
            r = (dy / s)**2
            if r <= RANGE**2:
                return (self.pos[0] - dy * c / s, wall[1]*th), r
            else:
                return (self.pos[0] + RANGE*c, self.pos[1] - RANGE*s), RANGE**2
            

    def get_vertices(self):
        tw, th = self.level.data.tilewidth, self.level.data.tileheight
        
        left = max(self.viewbox.left + self.dx, 0) / tw
        right = min((self.viewbox.right + self.dx) / tw, self.level.data.width-1)
        top = max(self.viewbox.top + self.dy, 0) / th
        bottom = min((self.viewbox.bottom + self.dy) / th, self.level.data.height-1)

        vertices = []
        
        for tx,ty in itertools.product(xrange(left, right+1), xrange(top, bottom+1)):
            if not self.level.passable[tx][ty]:
                for v in self.corners(tx, ty, left, right, top, bottom):
                    dx = v[0][0]*tw - self.pos[0]
                    dy = v[0][1]*tw - self.pos[1]
                    distance2 = dx**2 + dy**2
                    angle = normalise(math.atan2(-dy, dx) - self.facing)
                    vertices.append((angle, distance2, v[0], v[1]))

        return sorted(vertices)

    def corners(self, tx, ty, min_x, max_x, min_y, max_y):
        p = self.level.passable
        w, h = self.level.data.width, self.level.data.height

        l = r = t = b = True
        if tx-1 >= min_x:
            l = p[tx-1][ty]
        if tx+1 <= max_x:
            r = p[tx+1][ty]
        px = p[tx]
        if ty-1 >= min_y:
            t = px[ty-1]
        if ty+1 <= max_y:
            b = px[ty+1]

        if l and t:
            yield ((tx, ty), (1,0))
        elif not l and not t:
            if tx-1 < min_x or ty-1 < min_y or p[tx-1][ty-1]:
                yield ((tx, ty), (0,-1))
        if r and t:
            yield ((tx+1, ty), (0,1))
        elif not r and not t:
            if tx+1 > max_x or ty-1 < min_y or p[tx+1][ty-1]:
                yield ((tx+1, ty), (1,0))
        if r and b:
            yield ((tx+1, ty+1), (-1,0))
        elif not r and not b:
            if tx+1 > max_x or ty-1 > max_y or p[tx+1][ty+1]:
                yield ((tx+1, ty+1), (0,1))
        if l and b:
            yield ((tx, ty+1), (0,-1))
        elif not l and not b:
            if tx-1 < min_x or ty+1 > max_y or p[tx-1][ty+1]:
                yield ((tx, ty+1), (-1,0))

    #         start_time = pygame.time.get_ticks()
    #         start = self.facing - self.fov/2
    #         end = self.facing + self.fov/2
    #         angle = start
    #         sight = [] # (angle, distance, iswall, gridpos)
    #         heap = [] # (endangle, enddistance, wassolid, gridpos)
    #         visited = set()
    #         oldrange = 0
    #         # print("--------")
    #         while angle < end and pygame.time.get_ticks() - start_time < 1000:
    #             target = (end, RANGE, False, None)
    #             sight.append((angle, RANGE, False, None))
    #             for edge in self.castray(angle, oldrange):
    #                 heapq.heappush(heap, edge[1])
    #                 if edge[0][2]:
    #                     if edge[0][1] < sight[-1][1]:
    #                         sight[-1] = edge[0]
    #                         target = edge[1]
    #                     break
    #                 # print(sight)
    #                 # print(target)
    #                 # print(heap)
    #             while angle < target[0] and len(heap) > 0 and len(heap) < 1000 and pygame.time.get_ticks() - start_time < 1000:
    #                 #print("--")
    #                 p = heapq.heappop(heap)
    #                 if (angle, p[3]) in visited or p[1] > RANGE + 5*32:
    #                     continue
    #                 visited.add((angle, p[3]))
    #                 #print(p)
    #                 angle = p[0]
    #                 if angle > end or angle < start:
    #                     break
    #                 while angle >= target[0]:
    #                     # print("edge")
    #                     found = False
    #                     for edge in self.edges(target):
    #                         # print(edge)
    #                         if edge[0][2] and edge[0][1] < RANGE:
    #                             sight.append(edge[0])
    #                             target = edge[1]
    #                             found = True
    #                             break
    #                     if not found:
    #                         break
    #                 if angle < target[0]:
    #                     current = self.intersectray(angle,sight[-1],target)
    #                     for edge in self.edges(p):
    #                         heapq.heappush(heap, edge[1])
    #                         if edge[0][2]:
    #                             if edge[0][1] < current[1]:
    #                                 if edge[0][0] > sight[-1][0]:
    #                                     sight.append(current)
    #                                     sight.append(edge[0])
    #                                     target = edge[1]
    #                                 else:
    #                                     sight[-1] = edge[0]
    #                                     target = edge[1]
    #                             break
    #             angle = target[0]
    #             oldrange = target[1]
    #         # print("--------")
    #         sight.append(self.intersectray(end, sight[-1], target))
    #         self.polar = [(0,0,False, None)]
    #         self.sight = [(self.pos[0] - self.dx, self.pos[1] - self.dy)]
    #         old = (0,0,True,None)
    #         for p in sight:
    #             if not p[2] and not old[2]:
    #                 a = p[0] - old[0]
    #                 if a > math.pi:
    #                     a -= 2*math.pi
    #                 elif a < -math.pi:
    #                     a += 2*math.pi
    #                 a = p[0] - old[0]
    #                 n = max(int(60*a), 1)
    #                 da = a / n
    #                 self.sight += [(self.pos[0] - self.dx + p[1]*math.cos(old[0] + da*i), self.pos[1] - self.dy - p[1]*math.sin(old[0] + da*i)) for i in xrange(1,n)]
    #                 self.polar += [(old[0] + da*i, old[1], old[2], old[3]) for i in xrange(1,n)]
    #             self.sight.append((self.pos[0] - self.dx + p[1]*math.cos(p[0]), self.pos[1] - self.dy - p[1]*math.sin(p[0])))
    #             self.polar.append(p)
    #             old = p
    #         #self.sight = [self.pos]+[(self.pos[0] + p[1]*math.cos(p[0]), self.pos[1] + p[1]*math.sin(p[0])) for p in sight]

    def castray(self, angle, min_range):
        tw, th = self.level.data.tilewidth, self.level.data.tileheight
        x, y = self.pos
        dx, dy = math.cos(angle), -math.sin(angle)
        x += dx*min_range
        y += dy*min_range
        r = min_range
        done = False
        if dx == 0:
            if dy == 0:
                done = True
            else:
                if dy > 0:
                    dyr = (math.floor(y/th) + 1 - y/th)*th/dy
                else:
                    dyr = (math.ceil(y/th) - 1 - y/th)*th/dy
                y += dy * dyr
                r += dyr
                while True:
                    tx = int(math.floor(x/tw))
                    if dy > 0:
                        ty = int(math.floor(y/th))
                        end = (tx+1, ty)
                    else:
                        ty = int(math.ceil(y/th)) - 1
                        tx -= 1
                        end = (tx, ty+1)
                    x_diff = end[0]*tw - self.pos[0]
                    y_diff = end[1]*th - self.pos[1]
                    if tx < 0 or tx >= self.level.data.width or ty < 0 or ty >= self.level.data.height:
                        break
                    opaque = not self.level.transparent[tx][ty]
                    yield ((angle, r, opaque, (tx, ty)), (math.atan2(-y_diff, x_diff), math.sqrt(x_diff**2 + y_diff**2), opaque, (tx, ty)))
                    if dy > 0:
                        dyr = tw
                    else:
                        dyr = -tw
                    y += dyr
                    r += dyr/dy
        else:
            if dy == 0:
                if dx > 0:
                    dxr = (math.floor(x/th) + 1 - x/th)*th/dx
                else:
                    dxr = (math.ceil(x/th) - 1 - x/th)*th/dx
                x += dx * dxr
                r += dxr
                while True:
                    ty = int(math.floor(y/tw))
                    if dx > 0:
                        tx = int(math.floor(x/th))
                        ty -= 1
                        end = (tx, ty)
                    else:
                        tx = int(math.ceil(x/th)) - 1
                        end = (tx+1, ty+1)
                    x_diff = end[0]*tw - self.pos[0]
                    y_diff = end[1]*th - self.pos[1]
                    if tx < 0 or tx >= self.level.data.width or ty < 0 or ty >= self.level.data.height:
                        break
                    opaque = not self.level.transparent[tx][ty]
                    yield ((angle, r, opaque, (tx, ty)), (math.atan2(-y_diff, x_diff), math.sqrt(x_diff**2 + y_diff**2), opaque, (tx, ty)))
                    if dx > 0:
                        dxr = tw
                    else:
                        dxr = -tw
                    x += dxr
                    r += dxr/dx
        while not done:
            dxr = 0
            if dx > 0:
                dxr = (math.floor(x/tw) + 1 - x/tw)*tw/dx
            else:
                dxr = (math.ceil(x/tw) - 1 - x/tw)*tw/dx
            dyr = 0
            if dy > 0:
                dyr = (math.floor(y/th) + 1 - y/th)*th/dy
            else:
                dyr = (math.ceil(y/th) - 1 - y/th)*th/dy
            dr = min(dxr, dyr)
            x += dx * dr
            y += dy * dr
            r += dr
            tx = 0
            if dx > 0:
                tx = int(math.floor(x/tw))
            else:
                tx = int(math.ceil(x/tw)) - 1
            ty = 0
            if dy > 0:
                ty = int(math.floor(y/th))
            else:
                ty = int(math.ceil(y/th)) - 1
            if tx < 0 or tx >= self.level.data.width or ty < 0 or ty >= self.level.data.height:
                break
            opaque = not self.level.transparent[tx][ty]
            if dxr < dyr:
                if dx > 0:
                    end = (tx, ty)
                else:
                    end = (tx+1, ty+1)
                x_diff = end[0]*tw - self.pos[0]
                y_diff = end[1]*th - self.pos[1]
                yield ((angle, r, opaque, (tx, ty)), (math.atan2(-y_diff, x_diff), math.sqrt(x_diff**2 + y_diff**2), opaque, (tx, ty)))
            elif dyr < dxr:
                if dy > 0:
                    end = (tx+1, ty)
                else:
                    end = (tx, ty+1)
                x_diff = end[0]*tw - self.pos[0]
                y_diff = end[1]*th - self.pos[1]
                yield ((angle, r, opaque, (tx, ty)), (math.atan2(-y_diff, x_diff), math.sqrt(x_diff**2 + y_diff**2), opaque, (tx, ty)))
            else:
                if dx > 0:
                    if dy > 0:
                        end = (tx+1, ty)
                        tx2, ty2 = tx, ty-1
                        end2 = (tx2, ty2)
                    else:
                        end = (tx, ty)
                        tx2, ty2 = tx-1, ty
                        end2 = (tx2, ty2+1)
                else:
                    if dy > 0:
                        end = (tx+1, ty+1)
                        tx2, ty2 = tx+1, ty
                        end2 = (tx2+1, ty2)
                    else:
                        end = (tx, ty+1)
                        tx2, ty2 = tx, ty+1
                        end2 = (tx2+1, ty2+1)
                if tx2 < 0 or tx2 >= self.level.data.width or ty2 < 0 or ty2 >= self.level.data.height:
                    break
                opaque2 = not self.level.transparent[tx2][ty2]
                x_diff2 = end2[0]*tw - self.pos[0]
                y_diff2 = end2[1]*th - self.pos[1]
                yield ((angle, r, opaque2, (tx2, ty2)), (math.atan2(-y_diff2, x_diff2), math.sqrt(x_diff2**2 + y_diff2**2), opaque2, (tx2, ty2)))
                x_diff = end[0]*tw - self.pos[0]
                y_diff = end[1]*th - self.pos[1]
                yield ((angle, r, opaque, (tx, ty)), (math.atan2(-y_diff, x_diff), math.sqrt(x_diff**2 + y_diff**2), opaque, (tx, ty)))

    # def intersectray(self, angle, start, end):
    #     if not start[3] or not end[3]:
    #         return (angle, RANGE, False, None)
    #     else:
    #         if math.sin(end[0] - start[0]) != 0 and end[1] != 0:
    #             den = (math.sin(angle - start[0])*((start[1]/end[1]) - math.cos(end[0] - start[0]))/math.sin(end[0] - start[0]) + math.cos(angle - start[0]))
    #             if den != 0:
    #                 r = start[1] / den
    #             else:
    #                 r = RANGE
    #         else:
    #             r = 0
    #         return (angle, min(r, RANGE), start[2], start[3])

    # def edges(self, corner):
    #     tw, th = self.level.data.tilewidth, self.level.data.tileheight
    #     dx, dy = math.cos(corner[0]), -math.sin(corner[0])
    #     x, y = self.pos[0] + dx*corner[1], self.pos[1] + dy*corner[1]
    #     tx, ty = int(round(x/tw)), int(round(y/th))
    #     if dx < 0:
    #         tx -= 1
    #     if dy < 0:
    #         ty -= 1
    #     if dx > 0:
    #         if dy > 0:
    #             end = (tx+1, ty)
    #             tx2, ty2 = tx, ty-1
    #             end2 = (tx2, ty2)
    #         elif dy < 0:
    #             end = (tx, ty)
    #             tx2, ty2 = tx-1, ty
    #             end2 = (tx2, ty2+1)
    #         else:
    #             ty -= 1
    #             end = (tx, ty)
    #     elif dx < 0:
    #         if dy > 0:
    #             end = (tx+1, ty+1)
    #             tx2, ty2 = tx+1, ty
    #             end2 = (tx2+1, ty2)
    #         elif dy < 0:
    #             end = (tx, ty+1)
    #             tx2, ty2 = tx, ty+1
    #             end2 = (tx2+1, ty2+1)
    #         else:
    #             end = (tx+1, ty+1)
    #     else:
    #         if dy > 0:
    #             end = (tx+1, ty)
    #         elif dy < 0:
    #             tx -= 1
    #             end = (tx, ty+1)
    #         else:
    #             end = (tx, ty)
    #     if dx != 0 and dy != 0:
    #         if tx2 >= 0 and tx2 < self.level.data.width and ty2 >= 0 and ty2 < self.level.data.height:
    #             opaque2 = not self.level.transparent[tx2][ty2]
    #             x_diff2 = end2[0]*tw - self.pos[0]
    #             y_diff2 = end2[1]*th - self.pos[1]
    #             yield ((corner[0], corner[1], opaque2, (tx2, ty2)), (math.atan2(-y_diff2, x_diff2), math.sqrt(x_diff2**2 + y_diff2**2), opaque2, (tx2, ty2)))
    #     if tx >= 0 and tx < self.level.data.width and ty >= 0 and ty < self.level.data.height:
    #         opaque = not self.level.transparent[tx][ty]
    #         x_diff = end[0]*tw - self.pos[0]
    #         y_diff = end[1]*th - self.pos[1]
    #         yield ((corner[0], corner[1], opaque, (tx, ty)), (math.atan2(-y_diff, x_diff), math.sqrt(x_diff**2 + y_diff**2), opaque, (tx, ty)))
        
    def draw(self, surface):
        self.surface = surface
        if self.viewbox.colliderect(self.screenRect):
            # pygame.draw.lines(surface, (50, 0, 100), True, [(x-self.dx, y-self.dy) for x, y in (self.pos,
            #                                                                                     (self.pos[0]+RANGE*math.cos(self.facing-self.fov/2), self.pos[1]-RANGE*math.sin(self.facing-self.fov/2)),
            #                                                                                     (self.pos[0]+RANGE*math.cos(self.facing+self.fov/2), self.pos[1]-RANGE*math.sin(self.facing+self.fov/2)),
            #                                                                                 )], 2)
            pygame.draw.lines(surface, (0, 100, 0), True, self.sight, 1)
        
    def next_point(self):
        self.currentpoint += self.pointdelta
        if self.currentpoint >= len(self.points) or self.currentpoint < 0:
            if self.closed:
                self.currentpoint = 0
            else:
                self.pointdelta *= -1
                self.currentpoint += 2*self.pointdelta


    def cansee(self, other):
        # print("cansee")
        if not self.polar:
            # print("no polar")
            return False
        if ((self.pos[0] - other.pos[0])**2 + (self.pos[1] - other.pos[1])**2) > (RANGE + other.rect.height + other.rect.width)**2:
            # print("out of range")
            return False
        angles = [math.atan2(-(y - self.pos[1] + self.dy), x - self.pos[0] + self.dx) - self.facing for x,y in (other.rect.topleft, other.rect.topright, other.rect.bottomright, other.rect.bottomleft)]
        for i in xrange(len(angles)):
            if angles[i] < -math.pi:
                angles[i] += 2*math.pi
            elif angles[i] > math.pi:
                angles[i] -= 2*math.pi
        distance2 = [(x - self.pos[0] + self.dx)**2 + (y - self.pos[1] + self.dy)**2 for x,y in (other.rect.topleft, other.rect.topright, other.rect.bottomright, other.rect.bottomleft)]
        minangle = min(angles)
        maxangle = max(angles)
        mindist = min(distance2)
        jl = -1
        jh = -1
        for i in xrange(1, len(self.polar)):
            if jl == -1 and self.polar[i][0] > minangle:
                jl = i - 1
            if jl != -1:
                for j in xrange(len(angles)):
                    if self.polar[i][0] > angles[j] and self.polar[i-1][0] < angles[j]:
                        if interpolate_line(self.polar[i-1], self.polar[i], angles[j])[1] > distance2[j]:
                            # print("vertex "+str(j)+" in range")
                            return True
                if self.polar[i][0] > maxangle:
                    jh = i
                    break
        if jl == -1 or jh == -1:
            # print("can't find indices")
            # print(jl, jh)
            return False
        vision = self.polar[jl:jh+1]
        if len(vision) < 2:
            # print("list too short")
            return False
        if max((p[1] for p in vision)) < mindist:
            # print("definitely too far away")
            return False
        points = self.sight[jl:jh+1]
        for i in xrange(len(points)-1):
            if intersect_line_rect(points[i], points[i+1], other.rect):
                # print("intersecting")
                return True
        # print("non-intersecting")
        return False

def interpolate_line(p1, p2, angle):
    a = math.sqrt(p1[1])
    b = math.sqrt(p2[1])
    s = math.sin(p2[0] - p1[0])
    if s == 0.0:
        return (angle, (p1[1]+p2[1])/2)
    d = math.sin(angle - p1[0]) * (a/b - math.cos(p2[0] - p1[0])) / s + math.cos(angle - p1[0])
    if d == 0.0:
        return (angle, 0)
    return (angle, (a/d)**2)

def intersect_line_rect(p1, p2, rect):
    bb = pygame.Rect(min(p1[0], p2[0]), min(p1[1], p2[1]), abs(p1[0] - p2[0]), abs(p1[1] - p2[1]))
    # print(bb, rect)
    # pygame.draw.lines(surface, (100, 100, 100), True, (bb.topleft, bb.topright, bb.bottomright, bb.bottomleft), 3)
    # pygame.draw.lines(surface, (100, 100, 100), True, (rect.topleft, rect.topright, rect.bottomright, rect.bottomleft), 3)
    if not bb.colliderect(rect):
        # print("non-intersecting bounding boxes")
        return False
    # print(p1, p2)
    rx = p2[0] - p1[0]
    ry = p2[1] - p1[1]
    if rx != 0:
        rxinv = 1.0 / rx
        rcsinv = -1.0 / (rx * rect.height)
        
        t = (rect.left - p1[0]) * rxinv
        u = ((p1[0] - rect.left)*ry - (p1[1]-rect.top)*rx) * rcsinv
        # print(t,u)
        if t >= 0 and t <= 1 and u >= 0 and u <= 1:
            return True
        
        t = (rect.right - p1[0]) * rxinv
        u = ((p1[0] - rect.right)*ry - (p1[1]-rect.top)*rx) * rcsinv
        # print(t,u)
        if t >= 0 and t <= 1 and u >= 0 and u <= 1:
            return True
        
    if ry != 0:
        ryinv = 1.0 / ry
        rcsinv = 1.0 / (ry * rect.width)
        
        t = (rect.top - p1[1]) * ryinv
        u = ((p1[0] - rect.left)*ry - (p1[1]-rect.top)*rx) * rcsinv
        # print(t,u)
        if t >= 0 and t <= 1 and u >= 0 and u <= 1:
            return True
        
        t = (rect.bottom - p1[1]) * ryinv
        u = ((p1[0] - rect.left)*ry - (p1[1]-rect.bottom)*rx) * rcsinv
        # print(t,u)
        if t >= 0 and t <= 1 and u >= 0 and u <= 1:
            return True

    return False
