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

        self.viewbox.center = self.rect.center

        if self.viewbox.colliderect(self.screenRect):
            start_time = pygame.time.get_ticks()
            start = self.facing - self.fov/2
            end = self.facing + self.fov/2
            angle = start
            sight = [] # (angle, distance, iswall, gridpos)
            heap = [] # (endangle, enddistance, wassolid, gridpos)
            visited = set()
            oldrange = 0
            # print("--------")
            while angle < end and pygame.time.get_ticks() - start_time < 1000:
                target = (end, RANGE, False, None)
                sight.append((angle, RANGE, False, None))
                for edge in self.castray(angle, oldrange):
                    heapq.heappush(heap, edge[1])
                    if edge[0][2]:
                        if edge[0][1] < sight[-1][1]:
                            sight[-1] = edge[0]
                            target = edge[1]
                        break
                    # print(sight)
                    # print(target)
                    # print(heap)
                while angle < target[0] and len(heap) > 0 and len(heap) < 1000 and pygame.time.get_ticks() - start_time < 1000:
                    #print("--")
                    p = heapq.heappop(heap)
                    if (angle, p[3]) in visited or p[1] > RANGE + 5*32:
                        continue
                    visited.add((angle, p[3]))
                    #print(p)
                    angle = p[0]
                    if angle > end or angle < start:
                        break
                    while angle >= target[0]:
                        # print("edge")
                        found = False
                        for edge in self.edges(target):
                            # print(edge)
                            if edge[0][2] and edge[0][1] < RANGE:
                                sight.append(edge[0])
                                target = edge[1]
                                found = True
                                break
                        if not found:
                            break
                    if angle < target[0]:
                        current = self.intersectray(angle,sight[-1],target)
                        for edge in self.edges(p):
                            heapq.heappush(heap, edge[1])
                            if edge[0][2]:
                                if edge[0][1] < current[1]:
                                    if edge[0][0] > sight[-1][0]:
                                        sight.append(current)
                                        sight.append(edge[0])
                                        target = edge[1]
                                    else:
                                        sight[-1] = edge[0]
                                        target = edge[1]
                                break
                angle = target[0]
                oldrange = target[1]
            # print("--------")
            sight.append(self.intersectray(end, sight[-1], target))
            self.polar = [(0,0,False, None)]
            self.sight = [(self.pos[0] - self.dx, self.pos[1] - self.dy)]
            old = (0,0,True,None)
            for p in sight:
                if not p[2] and not old[2]:
                    a = p[0] - old[0]
                    if a > math.pi:
                        a -= 2*math.pi
                    elif a < -math.pi:
                        a += 2*math.pi
                    a = p[0] - old[0]
                    n = max(int(60*a), 1)
                    da = a / n
                    self.sight += [(self.pos[0] - self.dx + p[1]*math.cos(old[0] + da*i), self.pos[1] - self.dy - p[1]*math.sin(old[0] + da*i)) for i in xrange(1,n)]
                    self.polar += [(old[0] + da*i, old[1], old[2], old[3]) for i in xrange(1,n)]
                self.sight.append((self.pos[0] - self.dx + p[1]*math.cos(p[0]), self.pos[1] - self.dy - p[1]*math.sin(p[0])))
                self.polar.append(p)
                old = p
            #self.sight = [self.pos]+[(self.pos[0] + p[1]*math.cos(p[0]), self.pos[1] + p[1]*math.sin(p[0])) for p in sight]

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

    def intersectray(self, angle, start, end):
        if not start[3] or not end[3]:
            return (angle, RANGE, False, None)
        else:
            if math.sin(end[0] - start[0]) != 0 and end[1] != 0:
                den = (math.sin(angle - start[0])*((start[1]/end[1]) - math.cos(end[0] - start[0]))/math.sin(end[0] - start[0]) + math.cos(angle - start[0]))
                if den != 0:
                    r = start[1] / den
                else:
                    r = RANGE
            else:
                r = 0
            return (angle, min(r, RANGE), start[2], start[3])

    def edges(self, corner):
        tw, th = self.level.data.tilewidth, self.level.data.tileheight
        dx, dy = math.cos(corner[0]), -math.sin(corner[0])
        x, y = self.pos[0] + dx*corner[1], self.pos[1] + dy*corner[1]
        tx, ty = int(round(x/tw)), int(round(y/th))
        if dx < 0:
            tx -= 1
        if dy < 0:
            ty -= 1
        if dx > 0:
            if dy > 0:
                end = (tx+1, ty)
                tx2, ty2 = tx, ty-1
                end2 = (tx2, ty2)
            elif dy < 0:
                end = (tx, ty)
                tx2, ty2 = tx-1, ty
                end2 = (tx2, ty2+1)
            else:
                ty -= 1
                end = (tx, ty)
        elif dx < 0:
            if dy > 0:
                end = (tx+1, ty+1)
                tx2, ty2 = tx+1, ty
                end2 = (tx2+1, ty2)
            elif dy < 0:
                end = (tx, ty+1)
                tx2, ty2 = tx, ty+1
                end2 = (tx2+1, ty2+1)
            else:
                end = (tx+1, ty+1)
        else:
            if dy > 0:
                end = (tx+1, ty)
            elif dy < 0:
                tx -= 1
                end = (tx, ty+1)
            else:
                end = (tx, ty)
        if dx != 0 and dy != 0:
            if tx2 >= 0 and tx2 < self.level.data.width and ty2 >= 0 and ty2 < self.level.data.height:
                opaque2 = not self.level.transparent[tx2][ty2]
                x_diff2 = end2[0]*tw - self.pos[0]
                y_diff2 = end2[1]*th - self.pos[1]
                yield ((corner[0], corner[1], opaque2, (tx2, ty2)), (math.atan2(-y_diff2, x_diff2), math.sqrt(x_diff2**2 + y_diff2**2), opaque2, (tx2, ty2)))
        if tx >= 0 and tx < self.level.data.width and ty >= 0 and ty < self.level.data.height:
            opaque = not self.level.transparent[tx][ty]
            x_diff = end[0]*tw - self.pos[0]
            y_diff = end[1]*th - self.pos[1]
            yield ((corner[0], corner[1], opaque, (tx, ty)), (math.atan2(-y_diff, x_diff), math.sqrt(x_diff**2 + y_diff**2), opaque, (tx, ty)))
        
    def draw(self, surface):
        if self.viewbox.colliderect(self.screenRect):
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
        if not self.polar:
            return False
        if ((self.pos[0] - other.pos[0])**2 + (self.pos[1] - other.pos[1])**2) > RANGE**2:
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
        maxdist = max(distance2)
        jl = -1
        jh = -1
        for i in xrange(1, len(self.polar)):
            angle = self.polar[i][0] - self.facing
            if angle < -math.pi:
                angle += 2*math.pi
            elif angle > math.pi:
                angle -= 2*math.pi
            if jl == -1 and angle > minangle:
                jl = i - 1
            if jl != -1 and angle > maxangle:
                jh = i
                break
        if jl == -1 or jh == -1:
            return False
        vision = self.polar[jl:jh+1]
        if len(vision) < 2:
            return False
        if max((p[1] for p in vision))**2 < mindist:
            return False
        if min((p[1] for p in vision))**2 > maxdist:
            return True
        points = self.sight[jl:jh+1]
        for i in xrange(len(points)-1):
            if intersect_line_rect(points[i], points[i+1], other.rect):
                return True
        return False

def intersect_line_rect(p1, p2, rect):
    bb = pygame.Rect(min(p1[0], p2[0]), min(p1[1], p2[1]), abs(p1[0] - p2[0]), abs(p1[1] - p2[1]))
    if not bb.colliderect(rect):
        return False
    rx = p1[0] - p2[0]
    ry = p1[1] - p2[1]
    if rx != 0:
        rxinv = 1.0 / rx
        rcsinv = 1.0 / (rx * rect.height)
        
        t = (p1[0] - rect.left) * rxinv
        u = ((p1[0] - rect.left)*ry - (p1[1]-rect.top)*rx) * rcsinv
        if t >= 0 and t <= 1:
            return True
        
        t = (p1[0] - rect.right) * rxinv
        u = ((p1[0] - rect.right)*ry - (p1[1]-rect.top)*rx) * rcsinv
        if t >= 0 and t <= 1:
            return True
        
    if ry != 0:
        ryinv = 1.0 / ry
        rcsinv = 1.0 / (ry * rect.width)
        
        t = (p1[0] - rect.top) * ryinv
        u = ((p1[0] - rect.left)*ry - (p1[1]-rect.top)*rx) * rcsinv
        if t >= 0 and t <= 1:
            return True
        
        t = (p1[0] - rect.bottom) * ryinv
        u = ((p1[0] - rect.left)*ry - (p1[1]-rect.bottom)*rx) * rcsinv
        if t >= 0 and t <= 1:
            return True

    return False
