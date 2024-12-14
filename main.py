import pygame
from pygame.locals import *
import math
import asyncio

def get_text(text: str, color: str, size: int) -> pygame.Surface:
    font = pygame.font.SysFont('Sans Serif', size)
    return font.render(text, True, pygame.Color(color))

def to_blit(point):
    return [point[0], 800 - point[1]]

class vector:
#   __slots__ = ('x', 'y')
    def __init__(self, x, y = 0):
        if type(x) == tuple:
            x, y = x[0], x[1]
        self.x = float(x)
        self.y = float(y)
    def __repr__(self):
        return "vector"+str((self.x, self.y))
    #vector addition/subtraction
    def __add__(self, other):
        return vector(self.x+other.x, self.y+other.y)
    def __sub__(self, other):
        return vector(self.x-other.x, self.y-other.y)
    def __iadd__(self,other):
        self.x += other.x; self.y += other.y
        return self
    def __isub__(self,other):
        self.x -= other.x; self.y -= other.y
        return self
    #scalar multiplication/division
    def __mul__(self, other):
        if isinstance(other, vector):
            return dot(self, other)
        else: return vector(self.x*other, self.y*other)
    def __truediv__(self, other):
        return vector(self.x/other, self.y/other)
    def __imul__(self,other):
        self.x *= other; self.y *= other
        return self
    def __idiv__(self, other):
        self.x /= other; self.y /= other
        return self
    def magnitude(self):
        return distance((self.x, self.y), (0,0))
    def normalize(self):
        if (self.x, self.y) == (0,0): return vector(0,0)
        else: return self/self.magnitude()
    def rotate(self, other):
        x = self.x*math.cos(other) - self.y*math.sin(other)
        y = self.x*math.sin(other) + self.y*math.cos(other)
        return vector(x, y)
    def angle(self):
        return math.atan2(self.y, self.x)
    def draw(self) -> list:
        return [self.x, 400-self.y]

def det(a, b, c, d):
    # | a b |
    # | c d |
    return a*d - b*c

def distance2(p, q):
    if isinstance(p, vector) and isinstance(q, vector):
        return (p.x-q.x)**2 + (p.y-q.y)**2
    else:
        return (p[0]-q[0])**2 + (p[1]-q[1])**2

def distance(p, q):
    return distance2(p, q)**0.5
        
def dot(u, v):
    return u.x*v.x + u.y*v.y

def cross(u, v):
    return det(u.x, u.y, v.x, v.y)

async def main():
    pygame.init()

    WIDTH = 1000
    HEIGHT = 800
    screen = pygame.display.set_mode([WIDTH, HEIGHT])
    timer = pygame.time.Clock()
    fps = 80

    G = 100

    MASS = 10
    DIST_WHEEL = 40
    MOMENT = 2*0.5*MASS*0.25*(DIST_WHEEL**2)
    RADIUS_WHEEL = 8

    RANGE_CONSTANT = 100

    pos_cm = vector(100.0, 100.0)
    vel_cm = vector(0.0, 0.0)
    rotation = 0.0
    ang_vel = 0.0


    terrain = lambda x: 400-30*math.sin(0.03*x)
    

    counter = 0
    elapsed = 0

    running = True
    while running:
        # events

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # update logic
                


        ## pos_lr
        pos_l = vector(pos_cm.x-0.5*DIST_WHEEL*math.cos(rotation), pos_cm.y-0.5*DIST_WHEEL*math.sin(rotation))
        pos_r = vector(pos_cm.x+0.5*DIST_WHEEL*math.cos(rotation), pos_cm.y+0.5*DIST_WHEEL*math.sin(rotation))


        # draw
        screen.fill('black')
        text_surface = get_text(str(elapsed), 'white', 50)
        screen.blit(text_surface, (100, 100))

        for x in range(0, WIDTH-1):
            pygame.draw.line(screen, 'white', (x, terrain(x)), (x+1, terrain(x+1)), 4)

        ## bike
        pygame.draw.circle(screen, 'white', pos_l.draw(), RADIUS_WHEEL)
        pygame.draw.circle(screen, 'yellow', pos_r.draw(), RADIUS_WHEEL)
        pygame.draw.line(screen, 'white', pos_l.draw(), pos_r.draw(), 3)


        pygame.display.flip()


        # manage time
        timer.tick(fps)
        counter += 1
        elapsed += timer.get_time() * 0.001



        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
