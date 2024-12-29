from collections import deque
from random import choice, random
import sys
import pygame
import pymunk
import asyncio
import math
import time


def blit_rotated_circle(screen, circle_image, x, y, angle):
    rotated_image = pygame.transform.rotate(circle_image, angle)
    rotated_rect = rotated_image.get_rect(center=(x, y))
    screen.blit(rotated_image, rotated_rect)

def get_text(text:str, color:str, size:int) -> pygame.Surface:
    font = pygame.font.Font('Orbitron-Black.ttf', size)
    return font.render(text, True, color)

def grad_color(c:tuple):
    r, g, b = c
    return ((0.2*r, 0.2*g, 0.2*b), (0.4*r, 0.4*g, 0.4*b), (0.6*r, 0.6*g, 0.6*b), (0.8*r, 0.8*g, 0.8*b), c)

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
        return math.atan2(self.y, self.x)  # safer than math.atan(.../...)
    def Tuple(self):
        return (self.x, self.y)
        
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
    run_game = True

    WIDTH = 1400
    HEIGHT = 800
    screen = pygame.display.set_mode([WIDTH, HEIGHT])
    timer = pygame.time.Clock()
    fps = 100
    counter = 0

    first = True


    while run_game:

        ### save previous user
        if first:
            first = False
        else:
            rinit= True
            while rinit:
                screen.fill('black')
                screen.blit(get_text(f'SCORE {score}', 'white', 70), (200, 300))
                if wait and counter%200<100:
                    screen.blit(get_text(f'CLICK TO MOVE ON', 'white', 30), (250, 500))

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run_game = False
                    if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                        rinit = False

                pygame.display.flip()
                counter += 1

                await asyncio.sleep(0)
            time.sleep(1)
            with open("score.tsv", "a") as f:
                f.write(f"{''.join(sid)}\t{score}\n")
        



        init = True
        sid = ['?', '?', '?', '?', '?']
        cursor = 0
        wait = False
        counter = 0
        while init:

            if cursor == 5:
                if ((sid[0] == '1' or sid[0] == '2' or sid[0] =='3') and sid[1]=='0' and 0<int(sid[2])<=7 and 0<=int(sid[3])<=3) or (sid[0] == '0' and sid[1] == '0' and sid[2] == '0' and sid[3] == '0' and sid[4] == '0'):
                    wait = True
                else:
                    sid = ['A', 'G', 'A', 'I', 'N']
                    cursor = 0
            screen.fill('black')
            screen.blit(get_text('MATH RIDER', 'cyan', 70), (250, 300))
            screen.blit(get_text(f'STUDENT ID: {"".join(sid)}', 'white', 30), (250, 400))
            if wait and counter%200<100:
                screen.blit(get_text(f'CLICK TO START', 'white', 30), (250, 500))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run_game = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_0: sid[cursor] = "0"; cursor+=1
                    elif event.key == pygame.K_1: sid[cursor] = '1'; cursor+=1
                    elif event.key == pygame.K_3: sid[cursor] = '3'; cursor+=1
                    elif event.key == pygame.K_4: sid[cursor] = '4'; cursor+=1
                    elif event.key == pygame.K_5: sid[cursor] = '5'; cursor+=1
                    elif event.key == pygame.K_6: sid[cursor] = '6'; cursor+=1
                    elif event.key == pygame.K_7: sid[cursor] = '7'; cursor+=1
                    elif event.key == pygame.K_8: sid[cursor] = '8'; cursor+=1
                    elif event.key == pygame.K_9: sid[cursor] = '9'; cursor+=1
                    elif event.key == pygame.K_2: sid[cursor] = '2'; cursor+=1
                if event.type == pygame.MOUSEBUTTONDOWN and wait or event.type == pygame.KEYDOWN and wait:
                    init = False



            pygame.display.flip()
            counter += 1

            await asyncio.sleep(0)

        INIT_X = 150
        INIT_Y = 100
        OFFSET = 300

        MASS = 10
        THRUST = 160000
        ROTATIONAL_THRUST = 170000
        GRAVITY = 500
        RADIUS_WHEEL = 10
        DIST_WHEEL = 75

        SPEED_LIMIT = 17

        STEP = 10

        wheel = pygame.transform.scale((pygame.image.load("wheel.png")), (100, 100))

        g_green = grad_color((0, 255, 0))
        g_yellow = grad_color((255, 255, 0))
        g_magenta = grad_color((255, 0, 255))

        color_track = grad_color(choice([(255, 0, 255), (66, 135, 245), (87, 0, 186), (102, 255, 0), (252, 199, 38)]))
        track = deque()

        space = pymunk.Space()
        space.gravity = (0, GRAVITY)

    ######################
    #    bike wheels     #
    ######################

        front = pymunk.Body(MASS, 500, pymunk.Body.DYNAMIC)
        front.position = (INIT_X, INIT_Y)
        front_shape = pymunk.Circle(front, RADIUS_WHEEL)
        front_shape.density = 1
        front_shape.elasticity = 0.0
        front_shape.friction = 0.4
        
        back = pymunk.Body(MASS, 500, pymunk.Body.DYNAMIC)
        back.position = (INIT_X+DIST_WHEEL, INIT_Y)
        back_shape = pymunk.Circle(back, RADIUS_WHEEL)
        back_shape.density = 1
        back_shape.elasticity = 0.0
        back_shape.friction = 0.4
        
        frame = pymunk.constraints.PinJoint(front, back)

    #################
    #   bike hull   #
    #################
        COLLTYPE_LASER = 4
        COLLTYPE_WHEEL_F = 1
        COLLTYPE_WHEEL_B = 3
        COLLTYPE_TERRAIN = 2


    # types of terrains: 
    # - flat
    # - x**2 ramp
    # - sine mountain
    # - half-circle tracks
    # - three shallow mid-air bowls
    # - triangular
    # - sliced ramps /  /  /  /
    # - exp(x)-0 cliffs
    # - rings
    # - straight ramp


        t1 = lambda x:600-100-80*math.sin(0.01*x)
        t2 = lambda x:600-100-200*math.sin(0.004*x)

        # def _t2(x):
        #     if 0<=x<200:
        #         return None
        #     elif 200<=x<340:
        #         return 600-1.72*(x-350)-300
        #     elif 340<=x<
        #     elif 360<=x<500:
        #         return 600+1.72*(x-350)-300
        #     else:
        #         return None


        terrain = t1


        i = 0
        for x in range(0, WIDTH-1, STEP):
            if terrain(x) != None and terrain(x+STEP)!= None:
                trk_shape = pymunk.Segment(
                    space.static_body,
                    (x, terrain(x)),
                    (x+STEP, terrain(x+STEP)),
                    5
                )
                trk_shape.density = 1
                trk_shape.collision_type = COLLTYPE_TERRAIN
                trk_shape.user_data = i  
                trk_shape.elasticity = 0
                trk_shape.friction = 0.4
                track.append(trk_shape)
                space.add(trk_shape)
                i += 1

        front_shape.collision_type = COLLTYPE_WHEEL_F
        back_shape.collision_type = COLLTYPE_WHEEL_B

        hitb = False
        hitf = False

        colb = None
        colf = None

        timeb = 0.0
        timef = 0.0
        THRESH = 0.2


        def front_begin(arbiter, space, data):
            nonlocal hitf, timef, colf
            hitf = True
            timef = time.time()
            shape_a, shape_b = arbiter.shapes
            terrain_shape = shape_a if shape_a.collision_type == COLLTYPE_TERRAIN else shape_b
            colf = terrain_shape
            return True

        def front_separate(arbiter, space, data):
            nonlocal hitf, timef, colf
            t = time.time()
            if abs(t - timef) <= THRESH:
                timef = t
                return
            hitf = False
            colf = None

        def back_begin(arbiter, space, data):
            nonlocal hitb, timeb, colb
            hitb = True
            timeb = time.time()
            shape_a, shape_b = arbiter.shapes
            terrain_shape = shape_a if shape_a.collision_type == COLLTYPE_TERRAIN else shape_b
            colb = terrain_shape
            return True

        def back_separate(arbiter, space, data):
            nonlocal hitb, timeb, colb
            t = time.time()
            if abs(t - timeb) <= THRESH:
                timeb = t
                return
            hitb = False
            colb = None

        handler_f = space.add_collision_handler(COLLTYPE_WHEEL_F, COLLTYPE_TERRAIN)
        handler_b = space.add_collision_handler(COLLTYPE_WHEEL_B, COLLTYPE_TERRAIN)
        handler_death = space.add_collision_handler(COLLTYPE_LASER, COLLTYPE_WHEEL_B)
        handler_death2 = space.add_collision_handler(COLLTYPE_WHEEL_F, COLLTYPE_LASER)

        def _death(a, b, c):
            nonlocal running, god
            if not god: running = False
            return True
        handler_death.begin = _death
        handler_death2.begin = _death

        handler_f.begin = front_begin
        handler_f.separate = front_separate
        handler_b.begin = back_begin
        handler_b.separate = back_separate

        space.add(front, front_shape, back, back_shape, frame)

    ##########################
    #    types of terrains   #
    ##########################

        bo_before = 0
        fp_before = vector(front.position)


        click = False
        running = True

        flipping = False
        flipping_before = False
        start = None

        hit_time_f, hit_time_b = -1, -100

        hitf_before, hitb_before = False,False

        count = 0
        score = 0

        x_shift = 0
        y_shift = 0

        counter_show = -1
        counter_i = -1

        th2 = 1000
        th3 = 1000
        th4 = 1000

        god = False

        lasers = []

        saying = ""

        normal = vector(0, -1)
        normal_i = normal

        def relative(x):
            return (vector(x) - vector(front.position[0] - OFFSET, 0)).Tuple()

        while running:

            # switching terrains

            while track and (track[0].a[0] < front.position[0] - OFFSET-90):
                old_seg = track.popleft()
                space.remove(old_seg)
                if terrain(x) != None and terrain(x+STEP)!= None:
                    x = old_seg.a[0]+WIDTH
                    if round(x) % 400 == 0:
                        t_before = terrain
                        new_terrain = t2 if terrain == t1 else t1

                        old_val = t_before(x - x_shift) + y_shift
                        terrain = new_terrain
                        new_val = terrain(x - x_shift)

                        delta_y = old_val - new_val
                        y_shift = delta_y


                    trk_shape = pymunk.Segment(
                        space.static_body,
                        (x, terrain(x-x_shift)+y_shift),
                        (x+STEP, terrain(x+STEP-x_shift)+y_shift),
                        5
                    )
                    trk_shape.density = 1
                    trk_shape.collision_type = COLLTYPE_TERRAIN
                    trk_shape.user_data = len(track)
                    trk_shape.elasticity = 0.0
                    trk_shape.friction = 0.5
                    track.append(trk_shape)
                    space.add(trk_shape)

                    if random() < 0.007*(1+0.05*score):
                        if len(lasers)>0:
                            if front.position[0]-lasers[-1].body.position[0]>600:
                                laser = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
                                laser.position = ((vector(trk_shape.a)+vector(trk_shape.b))*0.5+vector(0, -100*random()-180)).Tuple()
                                laser_shape = pymunk.Circle(laser, 50)
                                laser_shape.collision_type = COLLTYPE_LASER
                                laser.user_data = laser.position[1]
                                space.add(laser, laser_shape)
                                lasers.append(laser_shape)
                        else:
                            laser = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
                            laser.position = ((vector(trk_shape.a)+vector(trk_shape.b))*0.5+vector(0, -180)).Tuple()
                            laser_shape = pymunk.Circle(laser, 50)
                            laser_shape.collision_type = COLLTYPE_LASER
                            space.add(laser, laser_shape)
                            lasers.append(laser_shape)


            # events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run_game = False
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    click = True
                if event.type == pygame.KEYUP or event.type == pygame.MOUSEBUTTONUP:
                    click = False
            


            # prevent 'collision hangovers'
            if colf != None:
                midf = (vector(colf.a)+vector(colf.b))*0.5
                if distance(midf, vector(front.position)) > 4*RADIUS_WHEEL:
                    hitf = False
            if colb != None:
                midb = (vector(colb.a)+vector(colb.b))*0.5
                if distance(midb, vector(back.position)) > 4*RADIUS_WHEEL:
                    hitb = False


            bike_orientation = (vector(front.position) - vector(back.position)).getAngle()
            omega = bike_orientation-bo_before

            if start != None:
                if bo_before <= start <= bike_orientation and omega>0:
                    count += 1


            speed = (vector(front.position)-fp_before).magnitude()

            # speed limit
            if hitb and colb != None:
                vb = (vector(colb.b) - vector(colb.a)).normalize() * THRUST*0.2*(SPEED_LIMIT-speed)
                if click: back.apply_force_at_world_point(vb.Tuple(), back.position)

            if hitf and colf != None:
                vf = (vector(colf.b) - vector(colf.a)).normalize() * THRUST*0.2*(SPEED_LIMIT-speed)#THRUST
                if click: front.apply_force_at_world_point(vf.Tuple(), front.position)

            if not hitf and not hitb and click and abs(omega)<0.08:
                rb = vector(-math.sin(bike_orientation),
                            math.cos(bike_orientation)) * ROTATIONAL_THRUST
                rf = rb * (-1)
                back.apply_force_at_world_point(rb.Tuple(), back.position)
                front.apply_force_at_world_point(rf.Tuple(), front.position)

            if not hitf and not hitb and not click and abs(omega)>0.03:
                rb = vector(math.sin(bike_orientation),
                -math.cos(bike_orientation)) * ROTATIONAL_THRUST
                rf = rb * (-1)
                back.apply_force_at_world_point(rb.Tuple(), back.position)
                front.apply_force_at_world_point(rf.Tuple(), front.position)
            if not hitf and not hitb and abs(omega)>0.12:
                rb = vector(math.sin(bike_orientation),
                -math.cos(bike_orientation))  *ROTATIONAL_THRUST * abs(omega)/omega
                rf = rb * (-1)
                back.apply_force_at_world_point(rb.Tuple(), back.position)
                front.apply_force_at_world_point(rf.Tuple(), front.position)

            if hitf and not hitf_before: # touchdown
                hit_time_f = time.time()
            if hitb and not hitb_before:
                hit_time_b = time.time()


            if not hitf and not hitb: # is flipping
                if not flipping_before: # start of flip
                    start = bike_orientation
                    count = 0
                flipping = True
            else:
                flipping = False
                if flipping_before: # end of flip
                    start = None
                    if abs(hit_time_f-hit_time_b) < 0.8 and count >= 2:
                        score += count*2
                        saying = "perfect flip! x2"
                    else:
                        score += count
                        if count >= 4:
                            saying = choice([f"maniac! +{count}", f"master at work! +{count}", "lunatic spinning!", 'insane flipping!', 'officially dizzy...'])
                        elif count ==3:
                            saying = choice(["flip streak!", "triple flip!"])
                        elif count==2:
                            saying = choice(["aced!", 'acing it!', 'crazy stunt!', 'daredevil!', 'double flip!'])
                        elif count==1:
                            saying = choice(["aced!", 'sweet!', 'wow!'])
                    counter_show = (counter + 200)
                    if count == 0: counter_show = -1
                    counter_i = counter
                    normal_i = normal



    
            flipping_before = flipping

            bo_before = bike_orientation
            fp_before = vector(front.position)

            # draw
            screen.fill('black')

            normal = vector(-math.sin(bike_orientation), math.cos(bike_orientation))
            point1 = (vector(front.position)+vector(back.position))*0.5 + normal*(0.05*DIST_WHEEL)
            point2 = vector(back.position)+normal*(0.25*DIST_WHEEL)
            point3 = (vector(front.position)+vector(back.position))*0.5 + normal*(0.4*DIST_WHEEL)
            point4 = vector(front.position)+normal*(0.25*DIST_WHEEL)
            pygame.draw.polygon(screen, 'blue', [relative(back.position), relative( point1.Tuple()), relative(front.position), relative(point4.Tuple()), relative(point3.Tuple()), relative(point2.Tuple())])






            for t in track:
                if distance(vector(t.a), vector(t.b)) < 2*STEP:
                    pygame.draw.line(screen, color_track[0], relative(t.a), relative(t.b), 38)
                    pygame.draw.line(screen, color_track[1], relative(t.a), relative(t.b), 30)
                    pygame.draw.line(screen, color_track[2], relative(t.a), relative(t.b), 24)
                    pygame.draw.line(screen, color_track[3], relative(t.a), relative(t.b), 16)
                    pygame.draw.line(screen, 'white', relative(t.a), relative(t.b), 8)
                

            for t in track:
                if distance(vector(t.a), vector(t.b)) < 2*STEP:
                    if t.a[0] <= point2.x < t.b[0]:
                        th2 = 0.5*(t.a[1]+t.b[1])
                    if t.a[0] <= point3.x < t.b[0]:
                        th3 = 0.5*(t.a[1]+t.b[1])
                    if t.a[0] <= point4.x < t.b[0]:
                        th4 = 0.5*(t.a[1]+t.b[1])
                    if terrain(point3.x-x_shift) != None and terrain(point2.x-x_shift) != None and terrain(point4.x-x_shift) != None:
                        if (point3.y+4 > th3 or point2.y+4 > th2 or point4.y+4>th4) and not god:
                            running = False


            for l in lasers:
                blit_posx, blit_posy = relative((l.body.position[0], l.body.position[1]))
                #pygame.draw.circle(screen,  (235, 101, 96), (blit_posx, blit_posy), 50)
                blit_rotated_circle(screen, wheel, blit_posx, blit_posy, counter*3)
                if blit_posx < -OFFSET:
                    lasers.remove(l)
                    space.remove(l)

            hitb_before = hitb
            hitf_before = hitf

            pygame.draw.circle(screen, 'white',
                (vector(front.position) - vector(front.position[0]-OFFSET, 0)).Tuple(),
                RADIUS_WHEEL
            )
            pygame.draw.circle(screen, 'white',
                (vector(back.position) - vector(front.position[0]-OFFSET, 0)).Tuple(),
                RADIUS_WHEEL
            )

            screen.blit(get_text(f"{score}", (100, 100, 100), 100), (0.5*(WIDTH-100), 10))
            if counter_show >= counter:
                screen.blit(get_text(saying, (255*(counter_show-counter)/(counter_show-counter_i), 255*(counter_show-counter)/(counter_show-counter_i), 255*(counter_show-counter)/(counter_show-counter_i)), 30),relative((vector(front.position)+normal_i*200).Tuple()))

            pygame.display.flip()

            # manage time
            space.step(1/fps)
            timer.tick(fps)
            counter += 1

            await asyncio.sleep(0)
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    asyncio.run(main())
