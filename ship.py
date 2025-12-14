import pygame
import math
import time
import random

from reynold import separation, cohesion, alignment, kelvin_cohesion, line_cohesion
import route
from utils.math_utils import line_intersection, line_from_points, point_in_segment, distance, vector_dot_product

TURN_FACTOR = .1
COASTLINE_TURN_FACTOR = 0.1
MARGIN = 0
RANGE = 5
MAX_VELOCITY = .7
# TODO: If ship velocity is this high, ship can clip through coastlines

SHIP_WIDTH = 5
SHIP_LENGTH = 10

SEPARATION_DISTANCE = 15
ALIGNMENT_DISTANCE = 80
COHESION_DISTANCE = 80

SEPARATION_FACTOR = 0.01
ALIGNMENT_FACTOR = 0.0001
COHESION_FACTOR = 0.05

ROUTE_FACTOR = 0.0005
ROUTE_WAYPOINT_DISTANCE = 40

LINE_FOLLOW_TIME = 3
LINE_FOLLOW_COASTLINE_THRESHOLD = 50


def find_velocity(route, ship_position):
    # route - pos
    rx, ry = route[-1]
    sx, sy = ship_position

    return rx - sx, ry - sy


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


def is_point_inside_segment(line_p1, line_p2, p3):
    # NOTE: maybe we should check distance by radius from point

    is_x_inside = p3[0] > min(line_p1[0], line_p2[0]) and p3[0] < max(line_p1[0], line_p2[0])
    is_y_inside = p3[1] > min(line_p1[1], line_p2[1]) and p3[1] < max(line_p1[1], line_p2[1])

    return is_x_inside or is_y_inside  # technically should be 'and', but shouldn't be a problem


class Ship:
    def __init__(self, x, y, route=None):
        self.x = x
        self.y = y
        self.vx = -1
        self.vy = -1
        self.route = route
        self.destination = None
        self.departure = None
        self.line_follow = False
        self.line_follow_timeout = time.time()

    def set_route(self, route):
        self.route = route.copy()

    # Draw the ship at its current position and orientation
    def draw(self, surface, debug_draw=False):
        # Create a ship surface with the long axis along +X (nose to the right)
        ship_surf = pygame.Surface((SHIP_LENGTH, SHIP_WIDTH), pygame.SRCALPHA)
        # Draw the ship rect, get.rect() to fill the entire surface
        color = "red" if self.line_follow else "black"
        pygame.draw.rect(ship_surf, color, ship_surf.get_rect())

        # Compute angle so the nose points along velocity (screen coords: y increases downward)
        if self.vx == 0 and self.vy == 0:
            angle_deg = 0.0
        else:
            angle_deg = math.degrees(math.atan2(-self.vy, self.vx))

        # Rotate and blit centered at (self.x, self.y)
        rotated = pygame.transform.rotate(ship_surf, angle_deg)
        rotated_rect = rotated.get_rect(center=(self.x, self.y))
        surface.blit(rotated, rotated_rect.topleft)

        # Optional debug velocity vector
        if debug_draw:
            pygame.draw.line(surface, "green", (self.x, self.y), (self.x + self.vx * 30, self.y + self.vy * 30))

    # Update velocity to stay within boundaries

    def boundary_update(self, w, h):
        if self.x > w - MARGIN:
            self.vx -= TURN_FACTOR
        if self.y > h - MARGIN:
            self.vy -= TURN_FACTOR
        if self.x < MARGIN:
            self.vx += TURN_FACTOR
        if self.y < MARGIN:
            self.vy += TURN_FACTOR

    def start_line_following(self, timeout):
        self.line_follow = True
        self.line_follow_timeout = timeout

    def line_follow_check(self, coastlines, surface=None):
        if self.line_follow:
            return

        theta = math.atan2(self.vy, self.vx)

        sensor_x = math.cos(theta + math.pi / 2) * LINE_FOLLOW_COASTLINE_THRESHOLD
        sensor_y = math.sin(theta + math.pi / 2) * LINE_FOLLOW_COASTLINE_THRESHOLD

        sensor_global_x = self.x + sensor_x
        sensor_global_y = self.y + sensor_y

        if surface is not None:
            pygame.draw.line(surface, "orange", (self.x, self.y), (self.x + sensor_x, self.y + sensor_y))
            pygame.draw.line(surface, "orange", (self.x, self.y), (self.x - sensor_x, self.y - sensor_y))

        a_r, b_r = line_from_points((self.x, self.y), (sensor_global_x, sensor_global_y))

        coastline_right_close = False
        coastline_left_close = False

        for coastline in coastlines:
            for p1, p2 in zip(coastline, coastline[1:]):
                line_a, line_b = line_from_points(p1, p2)

                intersection = line_intersection(a_r, b_r, line_a, line_b)

                if distance((self.x, self.y), intersection) > LINE_FOLLOW_COASTLINE_THRESHOLD:
                    continue
                
                if not point_in_segment(intersection, p1, p2):
                    continue
                
                if vector_dot_product((intersection[0] - self.x, intersection[1] - self.y), (sensor_global_x - self.x, sensor_global_y - self.y)) > 0:
                    coastline_right_close = True
                else:
                    coastline_left_close = True

        if coastline_right_close and coastline_left_close:
            self.start_line_following(time.time() + LINE_FOLLOW_TIME)

    def flocking(self, ships, surface=None):
        separation_neighbors = []
        alignment_neighbors = []
        cohesion_neighbors = []

        for other in ships:
            if other is self:
                continue

            d = distance((self.x, self.y), (other.x, other.y))

            # theta is the angle between two ships' route vectors
            theta = None  # Ships might not have a route
            # If both ships have routes, don't flock if route vectors differ by more than 90 degrees
            # NOTE: Maybe 90 degrees is not the optimal angle?
            if self.route is not None and other.route is not None:
                sx, sy = find_velocity(self.route, (self.x, self.y))
                ox, oy = find_velocity(other.route, (other.x, other.y))
                theta = sx * ox + sy * oy
            if d < SEPARATION_DISTANCE:
                separation_neighbors.append(other)
            if d < ALIGNMENT_DISTANCE and (theta is None or theta > 0):
                alignment_neighbors.append(other)
            if d < COHESION_DISTANCE and (theta is None or theta > 0):
                cohesion_neighbors.append(other)

        separation_vector = separation(self, separation_neighbors)
        alignment_vector = alignment(self, alignment_neighbors)
        cohesion_vector = cohesion(self, cohesion_neighbors)
        kelvin_vector = kelvin_cohesion(self, cohesion_neighbors, surface=surface)
        line_vector = line_cohesion(self, cohesion_neighbors, surface=surface)

        self.vx += separation_vector[0] * SEPARATION_FACTOR
        self.vy += separation_vector[1] * SEPARATION_FACTOR

        if alignment_vector is not None:
            self.vx += (alignment_vector[0] - self.vx) * ALIGNMENT_FACTOR
            self.vy += (alignment_vector[1] - self.vy) * ALIGNMENT_FACTOR

        # if cohesion_vector is not None:
        #     self.vx += (cohesion_vector[0] - self.x) * COHESION_FACTOR
        #     self.vy += (cohesion_vector[1] - self.y) * COHESION_FACTOR

        if self.line_follow and time.time() < self.line_follow_timeout:
            # Notify neighbors to also line follow
            for neighbor in cohesion_neighbors:
                if not neighbor.line_follow:
                    neighbor.start_line_following(self.line_follow_timeout)

            if line_vector is not None:
                self.vx += (line_vector[0] - self.x) * COHESION_FACTOR
                self.vy += (line_vector[1] - self.y) * COHESION_FACTOR
        else:
            if time.time() >= self.line_follow_timeout:
                self.line_follow = False

            if kelvin_vector is not None:
                self.vx += (kelvin_vector[0] - self.x) * COHESION_FACTOR
                self.vy += (kelvin_vector[1] - self.y) * COHESION_FACTOR

    def follow_route(self, surface=None):
        if self.route is None:
            return

        if len(self.route) >= 2 and distance((self.x, self.y), (self.route[-2])) < distance((self.x, self.y), (self.route[-1])):
            self.route.pop()

        # If route length is 1, we want to dock and therefore move as close to the point as possible
        if len(self.route) > 1 and distance((self.x, self.y), self.route[-1]) <= ROUTE_WAYPOINT_DISTANCE:
            self.route.pop()

        if len(self.route) == 0:
            self.route = None
            return

        dx, dy = find_velocity(self.route, (self.x, self.y))

        if surface is not None:
            pygame.draw.line(surface, "black", (self.x, self.y), self.route[-1])

        self.vx += dx * ROUTE_FACTOR
        self.vy += dy * ROUTE_FACTOR

    # Move ship, avoiding coastlines

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

        # Use target speed and go towards that instead
        velocity = math.sqrt(self.vx ** 2 + self.vy ** 2)
        if velocity > MAX_VELOCITY:
            factor = 1 / velocity * MAX_VELOCITY
            self.vx *= factor
            self.vy *= factor

        self.x += self.vx
        self.y += self.vy

    def dock(self, port):
        self.vx = 0
        self.vy = 0
        self.x = port.x
        self.y = port.y

    def undock(self, route=None):
        if route is not None:
            self.set_route(route.path)
            self.departure = route.departure
            self.destination = route.destination
        self.vx = 0
        self.vy = 0
        self.x = route.path[-2][0] + random.random() * 20 - 10
        self.y = route.path[-2][1] + random.random() * 20 - 10
