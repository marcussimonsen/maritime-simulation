import pygame
import math

TURN_FACTOR = .1
COASTLINE_TURN_FACTOR = 0.0001
MARGIN = 50
RANGE = 100
MAX_VELOCITY = .9

SHIP_WIDTH = 10
SHIP_LENGTH = 20

def line_from_points(p1, p2):
    a = (p2[1] - p1[1]) / (p2[0] - p1[0] + 1e-10)
    b = p1[1] - a * p1[0]
    return a, b

def closest_point(line, point):
    a, b = line
    x0, y0 = point

    x = (x0 + a * (y0 - b)) / (1 + a ** 2)
    y = a * x + b

    return x, y

def distance(point_a, point_b):
    ax, ay = point_a
    bx, by = point_b
    return math.sqrt((bx - ax) ** 2 + (by - ay) ** 2)


class Ship:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = -1
        self.vy = -1


    # TODO: Fix so rotation and scale is not off
    def draw(self, surface, debug_draw=False):
        # Ship rect
        rect = pygame.Rect(-SHIP_WIDTH / 2, -SHIP_LENGTH / 2, SHIP_WIDTH, SHIP_LENGTH)

        # Calculate angle in degrees of ship based on velocity
        angle = math.atan2(self.vy, math.sqrt(self.vx ** 2 + self.vy ** 2))
        angle = math.degrees(angle) + 90.

        # Create surface and draw the ship rect to that surface
        rect_surface = pygame.Surface((SHIP_WIDTH/2, SHIP_LENGTH/2), pygame.SRCALPHA)
        pygame.draw.rect(rect_surface, "black", rect)

        # Rotate surface according to the angle
        rotated_surface = pygame.transform.rotate(rect_surface, angle)

        # Draw rotated surface onto the screen "main" surface
        surface.blit(rotated_surface, (self.x, self.y))

        # Debug velocity draw
        if debug_draw:
            pygame.draw.line(surface, "green", (self.x, self.y), (self.x + self.vx * 30, self.y + self.vy * 30))

    def boundary_update(self, w, h):
        if self.x > w - MARGIN:
            self.vx -= TURN_FACTOR
        if self.y > h - MARGIN:
            self.vy -= TURN_FACTOR
        if self.x < MARGIN:
            self.vx += TURN_FACTOR
        if self.y < MARGIN:
            self.vy += TURN_FACTOR

    def move(self, ships, coastlines, surface=None):
        vx = 0
        vy = 0
        for coastline in coastlines:
            for p1, p2 in zip(coastline, coastline[1:]):
                c_line = line_from_points(p1, p2)

                point = closest_point(c_line, (self.x, self.y))
                x, y = point

                # Check if point inside coastline
                if x < min(p1[0], p2[0]):
                    if p1[0] < p2[0]:
                        x = p1[0]
                        y = p1[1]
                    else:
                        x = p2[0]
                        y = p2[1]
                elif x > max(p1[0], p2[0]):
                    if p1[0] > p2[0]:
                        x = p1[0]
                        y = p1[1]
                    else:
                        x = p2[0]
                        y = p2[1]

                point = x, y

                # Check if too far away
                if distance(point, (self.x, self.y)) > RANGE:
                    continue

                if surface is not None:
                    pygame.draw.circle(surface, "red", point, 3)

                if surface is not None:
                    pygame.draw.line(surface, "red", p1, p2)
                    pygame.draw.line(surface, "white", (self.x, self.y), point)

                # Steer away from coastline
                vx += self.x - x
                vy += self.y - y

        # NOTE: This is here because it is weird that further away gives stronger force
        # This gives constant force
        # Also good, since force then won't depend on granularity of coastline
        mag = math.sqrt(vx ** 2 + vy ** 2)
        if mag != 0:
            vx = vx / mag * 100
            vy = vy / mag * 100

        if surface is not None:
            pygame.draw.line(surface, "yellow", (self.x, self.y), (self.x + vx * 1, self.y + vy * 1))

        # Apply coastline effect
        self.vx += vx * COASTLINE_TURN_FACTOR
        self.vy += vy * COASTLINE_TURN_FACTOR

        velocity = math.sqrt(self.vx ** 2 + self.vy ** 2)
        if velocity > MAX_VELOCITY:
            factor = 1 / velocity * MAX_VELOCITY
            self.vx *= factor
            self.vy *= factor

        self.x += self.vx
        self.y += self.vy
