
import pygame
import pymunk
import asyncio
import math
import time

class vector(object):
    def __init__(self, x, y = 0):
        if type(x) == float or type(x) == int:
            self.x = float(x)
            self.y = float(y)
        else:
            self.x, self.y = x[0], x[1]
    def __repr__(self) -> str:
        return f"{self.x}i + {self.y}j"
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
    def getAngle(self):
        return math.atan(self.y / self.x)
    def Tuple(self):
        return (self.x, self.y)
        
# x**0.5 is annoying to compute, in python and in real life, it's a bit faster
def distance2(p, q):
    """distance squared between these points"""
    if isinstance(p, vector) and isinstance(q, vector):
        return (p.x-q.x)**2 + (p.y-q.y)**2
    else:
        return (p[0]-q[0])**2 + (p[1]-q[1])**2

def distance(p, q):
    """distance between these points"""
    return distance2(p, q)**0.5
        
def dot(u, v):
    """dot product of these vectors, a scalar"""
    return u.x*v.x + u.y*v.y


async def main():
    pygame.init()

    WIDTH = 1400
    HEIGHT = 800
    screen = pygame.display.set_mode([WIDTH, HEIGHT])
    timer = pygame.time.Clock()
    fps = 100
    counter = 0

    INIT_X = 150
    INIT_Y = 100
    OFFSET = 300

    THRUST = 100000
    ROTATIONAL_THRUST = 1000000
    GRAVITY = 750
    RADIUS_WHEEL = 10
    DIST_WHEEL = 50

    STEP = 10

    terrain = lambda x: 600-60*math.sin(0.008*x)-30*math.sin(0.012*x)
    track = []

    space = pymunk.Space()
    space.gravity = (0, GRAVITY)

    front = pymunk.Body(10, 100, pymunk.Body.DYNAMIC)
    front.position = (INIT_X, INIT_Y)
    front_shape = pymunk.Circle(front, RADIUS_WHEEL)
    front_shape.density = 1
    front_shape.elasticity = 0
    front_shape.friction = 0.2
    
    back = pymunk.Body(10, 100, pymunk.Body.DYNAMIC)
    back.position = (INIT_X+DIST_WHEEL, INIT_Y)
    back_shape = pymunk.Circle(back, RADIUS_WHEEL)
    back_shape.density = 1
    back_shape.elasticity = 0
    back_shape.friction = 0.2
    
    frame = pymunk.constraints.PinJoint(front, back)

    COLLTYPE_WHEEL_F = 1
    COLLTYPE_WHEEL_B = 3
    COLLTYPE_TERRAIN = 2

    i=0
    for x in range(0, WIDTH-1, STEP):
        trk_shape = pymunk.Segment(space.static_body, (x, terrain(x)), (x+STEP, terrain(x+STEP)), 5)
        trk_shape.density = 1
        trk_shape.collision_type = COLLTYPE_TERRAIN
        trk_shape.user_data = i
        trk_shape.elasticity = 0
        trk_shape.friction = 0.2
        track.append(trk_shape)
        space.add(trk_shape)
        i+=1



    front_shape.collision_type = COLLTYPE_WHEEL_F
    back_shape.collision_type = COLLTYPE_WHEEL_B
    trk_shape.collision_type = COLLTYPE_TERRAIN

    timeb = 0.0
    timef = 0.0


    THRESH = 0.07

    hitb = False
    hitf = False

    colb = None
    colf = None

    def front_begin(arbiter, space, data):
        nonlocal hitf, timef, colf
        hitf = True
        timef = time.time()
        shape_a, shape_b = arbiter.shapes

        wheel_shape = shape_a if shape_a.collision_type == COLLTYPE_WHEEL_F else shape_b
        terrain_shape = shape_b if shape_b.collision_type == COLLTYPE_TERRAIN else shape_a

        colf = terrain_shape.user_data

        return True

    def front_separate(arbiter, space, data):
        nonlocal hitf, timef, colf
        t = time.time()
        if abs(t-timef) <= THRESH:
            timef = t
            return
        hitf = False
        colf = None

    def back_begin(arbiter, space, data):
        nonlocal hitb, timeb, colb
        hitb = True
        timeb = time.time()
        shape_a, shape_b = arbiter.shapes

        wheel_shape = shape_a if shape_a.collision_type == COLLTYPE_WHEEL_B else shape_b
        terrain_shape = shape_b if shape_b.collision_type == COLLTYPE_TERRAIN else shape_a

        colb = terrain_shape.user_data
        return True

    def back_separate(arbiter, space, data):
        nonlocal hitb, timeb, colb
        t = time.time()
        if abs(t-timef) <= THRESH:
            return
        hitb = False
        colb = None
    def relative(x):
        nonlocal front
        return (vector(tuple(x))-vector(front.position[0]-OFFSET, 0)).Tuple()

    handler_f = space.add_collision_handler(COLLTYPE_WHEEL_F, COLLTYPE_TERRAIN)
    handler_b = space.add_collision_handler(COLLTYPE_WHEEL_B, COLLTYPE_TERRAIN)
    handler_f.begin = front_begin
    handler_f.separate = front_separate
    handler_b.begin = back_begin
    handler_b.separate = back_separate



    space.add(front, front_shape, back, back_shape, frame)

    click = False

    x_last = 0

    running = True
    while running:
        
        i=0
        for x in range(math.floor(x_last)+WIDTH, math.floor(front.position[0])+WIDTH, STEP):
            trk_shape = pymunk.Segment(space.static_body, (x, terrain(x)), (x+STEP, terrain(x+STEP)), 5)
            trk_shape.density = 1
            trk_shape.collision_type = COLLTYPE_TERRAIN
            trk_shape.user_data = i
            track.append(trk_shape)
            space.add(trk_shape)
            i+=1
        if math.floor(front.position[0])-math.floor(x_last) > STEP:
            x_last = front.position[0]

        # events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN or event.type==pygame.MOUSEBUTTONDOWN:
                click = True
            if event.type == pygame.KEYUP or event.type==pygame.MOUSEBUTTONUP:
                click = False
        
        # update
        if colb != None and click:
            vb = (vector(tuple(track[colb].b)) - vector(tuple(track[colb].a))).normalize() * THRUST
            back.apply_force_at_world_point(vb.Tuple(), back.position)

        if colf != None and click:
            vf = (vector(tuple(track[colf].b)) - vector(tuple(track[colf].a))).normalize() * THRUST
            front.apply_force_at_world_point(vf.Tuple(), front.position)

        # if colb != None and colf != None and click:
        #     # rotate
        #     bike_orientation = (vector(tuple(front.position))-vector(tuple(back.position))).getAngle()
        #     rb = vector(-round(abs(math.cos(bike_orientation)), 3), round(abs(math.sin(bike_orientation)), 3))*ROTATIONAL_THRUST
        #     rf = rb*(-1)
        #     print(rb, rf)
        #     back.apply_force_at_world_point(rb.Tuple(), back.position)
        #     front.apply_force_at_world_point(rf.Tuple(), front.position)



        # draw
        screen.fill('black')

        if hitf: color_f = 'cyan'
        else: color_f = 'white'
        if hitb: color_b = 'cyan'
        else: color_b = 'white'

        for t in track:
            pygame.draw.line(screen, (80, 12, 130), relative(t.a), relative(t.b), 16)
            pygame.draw.line(screen, (91, 17, 135), relative(t.a), relative(t.b), 30)
            pygame.draw.line(screen, (95, 19, 140), relative(t.a), relative(t.b), 24)
            pygame.draw.line(screen, (255, 255, 255), relative(t.a), relative(t.b), 8)
        
        pygame.draw.circle(screen, color_f, (vector(tuple(front.position))-vector(front.position[0]-OFFSET, 0)).Tuple(), RADIUS_WHEEL)
        pygame.draw.circle(screen, color_b, (vector(back.position)-vector(front.position[0]-OFFSET, 0)).Tuple(), RADIUS_WHEEL)



            

        pygame.display.flip()

        # manage time
        space.step(1/fps)
        timer.tick(fps)


        counter += 1

        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
