import pygame
from pygame.locals import *
import math
import asyncio

def get_text(text: str, color: str, size: int) -> pygame.Surface:
    font = pygame.font.SysFont('Sans Serif', size)
    return font.render(text, True, pygame.Color(color))

def to_blit(point):
    return [point[0], 800 - point[1]]

async def main():
    pygame.init()

    WIDTH = 1000
    HEIGHT = 800
    screen = pygame.display.set_mode([WIDTH, HEIGHT])
    timer = pygame.time.Clock()
    fps = 80

    G = 10

    MASS = 10
    DIST_WHEEL = 40
    MOMENT = 2*0.5*MASS*0.25*(DIST_WHEEL**2)
    RADIUS_WHEEL = 8

    RANGE_CONSTANT = 100

    pos_cm = [100.0, 30.0]
    vel_cm = [0.0, 0.0]
    forces = []
    pos_l = [-0.5*DIST_WHEEL, 0.0]
    pos_r = [0.0, 0.5*DIST_WHEEL]
    forces_l = []
    forces_r = []
    rotation = 0.0
    ang_vel = 0.0


    terrain = lambda x: 30*math.sin(0.5*x)
    

    counter = 0
    elapsed = 0

    running = True
    while running:
        # events

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # update logic
        
        ## compute forces_lr
        ### normal force
        #### sub: compute shortest distance
        minima = math.dist((-RANGE_CONSTANT+pos_l[0], terrain(-RANGE_CONSTANT+pos_l[0])), pos_l)
        critical = -RANGE_CONSTANT+pos_l[0]
        for x in range(-RANGE_CONSTANT+pos_l[0], RANGE_CONSTANT+pos_l[0]):
            new = math.dist((x, terrain(x)), pos_l)
            if minima > new:
                minima = new
                critical = x
        slope_ang = math.atan(terrain(critical+1)-terrain(critical))
        if slope_ang < 0: slope_ang += math.pi
        normal_mag = 0.5*MASS*G*math.cos(slope_ang+0.5*math.pi)
        if minima <= RADIUS_WHEEL:
            forces_l.append([normal_mag*math.cos(slope_ang+0.5*math.pi), normal_mag*math.sin(slope_ang+0.5*math.pi)]) # compute derivative ->`` normal force

        minima = math.dist((-RANGE_CONSTANT+pos_r[0], terrain(-RANGE_CONSTANT+pos_r[0])), pos_r)
        critical = -RANGE_CONSTANT+pos_r[0]
        for x in range(-RANGE_CONSTANT+pos_r[0], RANGE_CONSTANT+pos_r[0]):
            new = math.dist((x, terrain(x)), pos_r)
            if minima > new:
                minima = new
                critical = x
        slope_ang = math.atan(terrain(critical+1)-terrain(critical))
        if slope_ang < 0: slope_ang += math.pi
        normal_mag = 0.5*MASS*G*math.cos(slope_ang+0.5*math.pi)
        if minima <= RADIUS_WHEEL:
            forces_r.append([normal_mag*math.cos(slope_ang+0.5*math.pi), normal_mag*math.sin(slope_ang+0.5*math.pi)]) # compute derivative ->`` normal force

        ### gravity
        forces_r.append([0, -0.5*MASS*G])
        forces_l.append([0, -0.5*MASS*G])

        ## force and torque
        summed = [0.0, 0.0]
        torque = 0.0
        
        r_l = [pos_l[0]-pos_cm[0], pos_l[1]-pos_cm[1]]
        r_r = [pos_r[0]-pos_cm[0], pos_r[1]-pos_cm[1]]

        for force in forces_r:
            summed[0] += force[0]
            summed[1] += force[1]

            torque += math.sqrt([0, 0], force)*math.dist([0,0], r_r)*math.sin((force[0]*r_r[0]+force[1]*r_r[1])/abs(math.sqrt([0, 0], force)*math.dist([0,0], r_r)))
        for force in forces_l:
            summed[0] += force[0]
            summed[1] += force[1]
            torque += math.sqrt([0, 0], force)*math.dist([0,0], r_l)*math.sin((force[0]*r_l[0]+force[1]*r_l[1])/abs(math.sqrt([0, 0], force)*math.dist([0,0], r_l)))

        ## update position

        ang_vel += torque*elapsed/MOMENT
        rotation += ang_vel*elapsed + 0.5*torque*elapsed*elapsed/MOMENT

        vel_cm[0] += summed[0]*elapsed/MASS; vel_cm[1] += summed[1]*elapsed/MASS
        pos_cm[0] += vel_cm[0]*elapsed + 0.5*summed[0]*elapsed*elapsed/MOMENT
        pos_cm[1] += vel_cm[1]*elapsed + 0.5*summed[1]*elapsed*elapsed/MOMENT

        ## compute pos_lr

        pos_l = [pos_cm[0]-0.5*DIST_WHEEL*math.cos(rotation), pos_cm[1]-0.5*DIST_WHEEL*math.sin(rotation)]
        pos_r = [pos_cm[0]+0.5*DIST_WHEEL*math.cos(rotation), pos_cm[1]+0.5*DIST_WHEEL*math.sin(rotation)]


        # draw
        screen.fill('black')
        text_surface = get_text(str(timer.get_fps()), 'white', 50)
        screen.blit(text_surface, (100, 100))

        for x in range(0, WIDTH):
            x 

        pygame.display.flip()


        # manage time
        timer.tick(fps)
        counter += 1
        elapsed += timer.get_time() * 0.001



        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
