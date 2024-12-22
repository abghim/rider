import pygame
from pygame.locals import *
import math, copy
import asyncio



def get_text(text: str, color: str, size: int) -> pygame.Surface:
    font = pygame.font.SysFont('Sans Serif', size)
    return font.render(text, True, pygame.Color(color))

def to_blit(point):
    return [point[0], 800 - point[1]]
class vector(object):
    #slots for optimization...?
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
        """exception: if other is also a vector, DOT PRODUCT
            I do it all the time in my 3d calc hw anyways :|"""
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
    def magnitude2(self):
        """the square of the magnitude of this vector"""
        return distance2((self.x, self.y), (0,0))
    def magnitude(self):
        """magnitude of this vector)"""
        return distance((self.x, self.y), (0,0))
    def normalize(self):
        """unit vector. same direction but with a magnitude of 1"""
        if (self.x, self.y) == (0,0): return vector(0,0)
        else: return self/self.magnitude()
    def rotate(self, other):
        """rotates vector in radians"""
        x = self.x*math.cos(other) - self.y*math.sin(other)
        y = self.x*math.sin(other) + self.y*math.cos(other)
        return vector(x, y)
    def getAngle(self):
        """gets angle of vector relative to x axis"""
        return math.atan2(self.y, self.x)
    def draw(self):
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

def cross(u, v):
    """magnitude of the cross product of these vectors"""
    return det(u.x, u.y, v.x, v.y)

class Point(object):
    """points have position and velocity implied by previous position"""
    def __init__(self, *args):
        x, y = args[0], args[1]
        #current position
        self.r = vector(x, y)
        #position one frame before. no value, set to same as x,y
        if len(args) == 2:
            x0, y0 = x, y
        self.r0 = vector(x0, y0)
    def __repr__(self):
        return "Point"+str( (self.r, self.r0) )

class Circle(object):
    def __init__(self, center:vector, radius:int) -> None:
        self.center = Point(center.x, center.y)
        self.radius = radius
        self._acc = False
    def acc(self):
        self._acc = True
    def un_acc(self):
        self._acc = False


class Line(object):
    """lines are defined by two points, p1 and p2"""
#   __slots__ = ('r1', 'r2') #I ANTICIPATE THOUSANDS OF LINES
    def __init__(self, r1, r2):
    #points are position vectors
        if isinstance(r1, vector) and isinstance(r2, vector):
            self.r1 = r1
            self.r2 = r2
        else: #inputs are tuples
            self.r1 = vector(r1[0], r1[1])
            self.r2 = vector(r2[0], r2[1])
    def __repr__(self):
        return "Line"+str((self.r1, self.r2, self.lineType))
    def linearEquation(self):
        """in the form of ax+by=c"""
        a = self.r2.y - self.r1.y
        b = self.r1.x - self.r2.x
        c = a*self.r1.x + b*self.r1.y
        return a, b, c
def intersectPoint(line1, line2):
    """Returns the coordinates of intersection between line segments.
    If the lines are not intersecting, returns None.""" 
    a1,b1,c1 = line1.linearEquation()
    a2,b2,c2 = line2.linearEquation()
    d = det(a1, b1, a2, b2)
    if d == 0: return None
    x = 1.0*det(c1, b1, c2, b2)/d
    y = 1.0*det(a1, c1, a2, c2)/d
    intersection = vector(x, y)
    if (isInLineRegion(intersection, line1)
        and isInLineRegion(intersection, line2)):
        return intersection #position vector of point of intersection
        
def det(a, b, c, d):
    """determinant"""
    # | a b |
    # | c d |
    return a*d - b*c

def isInLineRegion(r, line):
    """rectangular region defined by endpoints of a line segment or points"""
    return isInRegion(r, line.r1, line.r2)


def isInRegion(r, pnt1, pnt2):
    if isinstance(pnt1, vector):
        x1, x2, y1, y2 = pnt1.x, pnt2.x, pnt1.y, pnt2.y
    else:
        x1, x2, y1, y2 = pnt1[0], pnt2[0], pnt1[1], pnt2[1]
    if isinstance(r, vector):
        rx, ry = r.x, r.y
    else:
        rx, ry = r[0], r[1]
    x1, x2 = min(x1, x2), max(x1, x2)
    y1, y2 = min(y1, y2), max(y1, y2)
    isInRect = x1<= rx <=x2 and y1<= ry <=y2
    isOnHLine = x1==x2 and almostEqual(x1,rx) and y1 <= ry <= y2
    isOnVLine = y1==y2 and almostEqual(y1,ry) and x1 <= rx <= x2
    return isInRect or isOnHLine or isOnVLine

def almostEqual(a, b):
    EPSILON = 0.0000000001
    return abs(a-b) < EPSILON/100

def closestPointOnLine(r, line:Line):
    """closest point on a line to a point(position vector)"""
    a, b, c1 = line.linearEquation()
    c2 = -b*r.x + a*r.y
    d = det(a, b, -b, a)
    if d == 0:
        point = r #POINT IS ON LINE
    else:
        x = det(a, b, c2, c1)/d
        y = det(a, -b, c1, c2)/d
        point = vector(x, y) #it's a position vector!
    return point
def distanceFromLine(r, line):
    """distance between a point and a line segment"""
    linePoint = closestPointOnLine(r, line)
    if isInLineRegion(linePoint, line):
        dist = distance(r, linePoint)
    else:
        dist = min(distance(r, line.r1), distance(r, line.r2))
    return dist

class solidLine(Line):
    """collidable lines"""
    def __init__(self, r1, r2):
        super(solidLine, self).__init__(r1, r2)
#       self.dir = (self.r2-self.r1).normalize() #direction the line points in
    #normal to line, 90 degrees ccw (to the left). DARN YOU FLIPPED COORDINATES
#       self.norm = vector(self.dir.y, -self.dir.x)
    def __repr__(self):
        return "solidLine"+str((self.r1, self.r2))



timeDelta = delta = 10 #100 hz/fps
grav = vector(0, 30.0/1000*delta) #pixels per frame**2
drag = 0.9999999**delta
acc = 0.1*delta #acceleration line constant
epsilon = 0.00000000001 #larger than floating point errors
lineThickness = 0.001
endurance = 0.4
gridSize = 50
iterations = 10
maxiter = 100
viewLines = True
viewVector = False
viewPoints = False
viewGrid = False
viewStatus = True
viewCollisions = False
viewThinLines = False
slowmo = False
follow = True
mouseEnable = True
center = vector(400,300)
topLeft = vector(0,0)
bottomRight = vector(800,600)
windowSize = vector(800,600)

    
# def resolveCollision(circle:Circle):
#     """takes a solid point, finds and resolves collisions,
#     and returns the acceleration lines it collided with"""
#     hasCollided = True
#     a = acc
#     maxiter = 100

#     while hasCollided == True and maxiter > 0:
#         hasCollided = False
# #get the lines the point may collide with
#         lines = getCollisionLines()
# #get the collision points of the lines the point actually collides with
#         collidingLines, collisionPoints, intersections = getCollidingLines(pnt, lines)
# #no collisions? break
#         if collisionPoints == []:
#             break
#         elif len(collisionPoints) >1:
# #more than one collision points: get the intersection point closest to the point
#             futurePoint = closestCollisionPoint(pnt, intersections, collisionPoints)
#             index=collisionPoints.index(futurePoint)
#             collidingLine = collidingLines[index]
#         else:
#             futurePoint = collisionPoints[0]
#             collidingLine = collidingLines[0]
# #set future point to above point, evaluate acc line if necessary
#         pnt.r = futurePoint

#         hasCollided = True
#         maxiter -= 1
#         if viewCollisions:
#            collisionPoints += [copy.copy(futurePoint)]

# #repeat if there was a collision

# def getCollidingLines(circle:Circle, lines):
#     """"returns a list of the lines "pnt" actually collides with
#         and the respective intersection points"""
#     collisionPoints = []
#     collidingLines = []
#     intersections = []
#     for line in lines:
#         point = getCollision(circle, line)
#         if point != None:
#             collidingLines += [line]
#             collisionPoints += [point[0]]
#             intersections += [point[1]]
#     return collidingLines, collisionPoints, intersections

# def getCollision(circle:Circle, line):
#     """returns the position after collision(if it exists)"""
#     trajectory = Line(circle.center.r, circle.center.r0)

#     intersection = intersectPoint(trajectory, line)
#     thickness = circle.radius+lineThickness + epsilon
#     if intersection != None:
#         #if intersecting, project position onto line
#         futurePos = closestPointOnLine(circle.center.r, line)
#         #line thickness
#         futurePos += (futurePos-circle.center.r).normalize()*thickness
# #        print("intersection!")
#         return futurePos, intersection
#     else: return None


# def closestPoint(pnt, points):
#     closestPoint = points[0] #first point
#     minDist = distance(closestPoint,pnt)
#     for point in points[1:]:
#         dist = distance(point,pnt)
#         if dist < minDist:
#             minDist = dist
#             closestPoint = point
#     return closestPoint

# def closestCollisionPoint(pnt, intersections, collisionPoints):
#     closestIntersection = closestPoint(pnt.r0, intersections)
#     i = intersections.index(closestIntersection)
#     return collisionPoints[i]

# def getCollisionLines(pnt):
#     """returns a set of lines that exist in the same cells as the point"""
#     vLine = Line(pnt.r0, pnt.r)
#     cells = getGridCells(vLine) #list of cell positions
#     lines = set()
#     solids = canvas.grid.solids
#     for gPos in cells:
#         cell = solids.get(gPos, set())
#         lines |= cell #add to set of lines to check collisions
#     return lines

def resolveCollision(circle: Circle):
    """
    Takes a circle, finds and resolves collisions by adjusting the circle's
    center position (circle.center.r) if it intersects with any lines.

    Returns nothing, but modifies circle.center.r in-place.
    """
    hasCollided = True
    maxiter = 100  # limit iterations to avoid infinite loops in deep penetrations

    while hasCollided and maxiter > 0:
        hasCollided = False

        # Get potential colliding lines (based on circle's movement)
        lines = getCollisionLines(circle)

        # Find which lines actually collide, and the respective collision points
        collidingLines, collisionPoints, intersections = getCollidingLines(circle, lines)

        # If no collisions, we're done this frame
        if len(collisionPoints) == 0:
            break
        
        # If multiple collisions, pick the one whose intersection is closest
        # to the circle's previous center (circle.center.r0)
        elif len(collisionPoints) > 1:
            futurePoint = closestCollisionPoint(circle, intersections, collisionPoints)
            index = collisionPoints.index(futurePoint)
            collidingLine = collidingLines[index]
        else:
            # Exactly one collision
            futurePoint = collisionPoints[0]
            collidingLine = collidingLines[0]

        # Reposition the circle center to avoid line penetration
        circle.center.r = futurePoint

        # Mark that we collided and try resolving again (in case multiple lines
        # or deeper penetrations require iterative resolution)
        hasCollided = True
        maxiter -= 1


def getCollidingLines(circle: Circle, lines):
    """
    Returns (collidingLines, collisionPoints, intersections):
      - collidingLines: list of line segments that 'circle' collides with
      - collisionPoints: where the circle center should move to avoid each collision
      - intersections: the intersection points (if any) on the lines
    """
    collisionPoints = []
    collidingLines = []
    intersections = []

    for line in lines:
        result = getCollision(circle, line)
        if result is not None:
            # result is (futurePos, intersection)
            futurePos, intersec = result
            collidingLines.append(line)
            collisionPoints.append(futurePos)
            intersections.append(intersec)

    return collidingLines, collisionPoints, intersections


def getCollision(circle: Circle, line):
    """
    Checks collision between the circle and a single line segment during
    the current frame's movement. Returns (futurePos, intersection) if collided,
    or None if no collision.

    futurePos: vector where circle.center.r should be placed to avoid the line.
    intersection: the line intersection point or a placeholder if not relevant.
    """
    # The circle center's movement this frame
    trajectory = Line(circle.center.r0, circle.center.r)
    intersection = intersectPoint(trajectory, line)

    # Effective thickness = circle radius + line thickness + epsilon
    # (If you only want the circle's radius, remove lineThickness from sum.)
    thickness = circle.radius + lineThickness + epsilon

    # 1) If the circle's path intersects the line segment
    if intersection is not None:
        # "Project" the circle center onto the line
        futurePos = closestPointOnLine(circle.center.r, line)
        # Then move outward along the normal by 'thickness'
        futurePos += (futurePos - circle.center.r).normalize() * thickness
        return (futurePos, intersection)
    
    # 2) If the circle center is within 'thickness' distance of the line,
    #    meaning it's "inside" the line boundary
    elif distanceFromLine(circle.center.r, line) < thickness:
        futurePos = closestPointOnLine(circle.center.r, line)
        # Move out in the opposite direction
        # (circle.center.r -> futurePos means we do futurePos += ...)
        futurePos += (circle.center.r - futurePos).normalize() * thickness
        return (futurePos, circle.center.r)

    # 3) No collision
    return None


def closestCollisionPoint(circle: Circle, intersections, collisionPoints):
    """
    Among multiple collision candidates, picks the collision whose line-intersection
    is closest to circle.center.r0 (the old position), then uses that to find the
    matching 'futurePos'.
    """
    oldPos = circle.center.r0  # the circle's previous center
    # Choose the intersection point nearest to oldPos
    closest_intersection = closestPoint(oldPos, intersections)
    i = intersections.index(closest_intersection)
    return collisionPoints[i]



def getCollisionLines(circle: Circle):
    """
    Return only those lines whose bounding box overlaps the circle's
    bounding box. This omits lines clearly too far away to collide.
    """
    lines_near = []
    # Suppose your track lines are stored in something like canvas.track.lines
    all_lines = track

    # Circle bounding box:
    cx, cy = circle.center.r.x, circle.center.r.y
    r = circle.radius
    circle_min_x = cx - r
    circle_max_x = cx + r
    circle_min_y = cy - r
    circle_max_y = cy + r

    for line in all_lines:
        min_x = min(line.r1.x, line.r2.x)
        max_x = max(line.r1.x, line.r2.x)
        min_y = min(line.r1.y, line.r2.y)
        max_y = max(line.r1.y, line.r2.y)

        # Check bounding box overlap:
        #  If the line's box is completely to one side of the circle's box,
        #  there's no possibility of collision.
        if (max_x < circle_min_x or
            min_x > circle_max_x or
            max_y < circle_min_y or
            min_y > circle_max_y):
            continue  # skip this line, no overlap

        # Otherwise, the bounding boxes overlap, so the line
        # might be near enough to collide:
        lines_near.append(line)

    return lines_near


def closestPoint(p: vector, pts: list):
    """
    Returns which vector in 'pts' is closest to 'p'.
    'pts' could be intersection points or line endpoints, etc.
    """
    if not pts:
        return None  # edge case, if no points given

    closest_pt = pts[0]
    minDist = distance(closest_pt, p)
    for pt in pts[1:]:
        distP = distance(pt, p)
        if distP < minDist:
            minDist = distP
            closest_pt = pt
    return closest_pt

class Constraint():
    def __init__(self, pnt1, pnt2, restLength):
        #p1 and p2 are points
        self.pnt1, self.pnt2 = pnt1, pnt2
        self.restLength = restLength
    def __repr__(self):
        return str((self.pnt1, self.pnt2, self.restLength))
        
def resolveConstraint(cnstr):
    """resolves a given constraint"""
    delta = cnstr.pnt1.r - cnstr.pnt2.r
    deltaLength = delta.magnitude()
    diff = (deltaLength-cnstr.restLength)/deltaLength
    cnstr.pnt1.r -= delta*diff/2
    cnstr.pnt2.r += delta*diff/2

async def main():
    pygame.init()

    WIDTH = 1000
    HEIGHT = 800
    screen = pygame.display.set_mode([WIDTH, HEIGHT])
    timer = pygame.time.Clock()
    fps = 40


    


    G = 2
    GRAVITY = vector(0, -G)

    MASS_WHEEL = 10
    DIST_WHEEL = 40
    MOMENT = 2*MASS_WHEEL*(DIST_WHEEL**2)
    RADIUS_WHEEL = 10

    RANGE_CONSTANT = 100

    front = vector(200, 720)
    back = vector(200+DIST_WHEEL, 720)



    terrain = lambda x: 400-100*math.sin(0.015*x)

    global track
    track = []
    for x in range(0, WIDTH-1, 5):
        track.append(solidLine((x, terrain(x)), (x+5, terrain(x+5))))
    print(len(track))    


    front = Circle(front, RADIUS_WHEEL)
    back = Circle(back, RADIUS_WHEEL)
    bike = Constraint(front.center, back.center, DIST_WHEEL)


    counter = 0
    elapsed = 0

    running = True
    while running:
    
        # events

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            

        # update logic
        
        def freefall(pnt:Point):
            velocity = pnt.r - pnt.r0
            pnt.r =  pnt.r + GRAVITY + velocity*0.8

        pastpos = front.center.r
        freefall(front.center)
        front.center.r0 = pastpos

        pastpos = back.center.r
        freefall(back.center)
        back.center.r0 = pastpos

        resolveConstraint(bike)

        resolveCollision(front)
        resolveCollision(back)

        # accelerations
        # rotations



        # draw
        screen.fill('black')
        text_surface = get_text(str(elapsed), 'white', 50)
        screen.blit(text_surface, (100, 100))

        for l in track:
            pygame.draw.line(screen, 'white', to_blit((l.r1.x, l.r1.y)), to_blit((l.r2.x, l.r2.y)), 4)

        pygame.draw.circle(screen, 'white', to_blit((front.center.r.x, front.center.r.y)), RADIUS_WHEEL)
        pygame.draw.circle(screen, 'white', to_blit((back.center.r.x, back.center.r.y)), RADIUS_WHEEL)
        pygame.draw.line(screen, 'white', to_blit((front.center.r.x, front.center.r.y)), to_blit((back.center.r.x, back.center.r.y)), 6)

        pygame.display.flip()


        # manage time
        timer.tick(fps)
        counter += 1




        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
