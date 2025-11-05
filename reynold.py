import math
import time

import pygame

from utils import vector_dot_product, distance

def alignment(ship, neighbors) -> tuple[float, float]|None:
    avg_velx = 0
    avg_vely = 0

    for other in neighbors:
        avg_velx += other.vx
        avg_vely += other.vy

    if len(neighbors) > 0:
        avg_velx /= len(neighbors)
        avg_vely /= len(neighbors)

        return avg_velx, avg_vely
    else:
        return None


def separation(ship, neighbors) -> tuple[float, float]:
    x = 0
    y = 0

    for other in neighbors:
        x +=  (ship.x - other.x + 1e-12)
        y +=  (ship.y - other.y + 1e-12)

    return x, y

def cohesion(ship, neighbors) -> tuple[float, float]|None:
    avg_posx = 0
    avg_posy = 0

    for other in neighbors:
        avg_posx += other.x
        avg_posy += other.y

    if len(neighbors) > 0:
        avg_posx /= len(neighbors)
        avg_posy /= len(neighbors)

        return avg_posx, avg_posy
    else:
        return None


def kelvin_cohesion(ship, neighbors, surface=None):
    # Find closest neighbor that is in front
    # Place current ship 35 degrees to the left or right behind the front ship and XX behind
    closest_neighbor = None
    closest_dist = float('inf')

    for other in neighbors:
        # Check if ship is in front
        if vector_dot_product((ship.vx, ship.vy), (other.x - ship.x, other.y - ship.y)) <= 0:
            continue

        # Check if ships are heading in same direction (less than 90 degrees difference)
        if vector_dot_product((ship.vx, ship.vy), (other.vx, other.vy)) <= 0:
            continue

        # Find closest neighbor
        d = distance((ship.x, ship.y), (other.x, other.y))
        if d < closest_dist:
            closest_dist = d
            closest_neighbor = other

    if closest_neighbor is None:
        return None

    # Angle of neighbors heading
    theta_v = math.atan(closest_neighbor.vy / closest_neighbor.vx)
    if closest_neighbor.vx > 0:
        theta_v = theta_v + math.pi

    # Hyperparameters for tuning Kelvin angle
    kelvin_distance = 25.
    kelvin_angle = 35

    # Angle of follow points
    theta_l = theta_v + math.radians(kelvin_angle)
    theta_r = theta_v - math.radians(kelvin_angle)

    # x pos of follow point relative to neighbor ship
    dx_l = math.cos(theta_l) * kelvin_distance
    dx_r = math.cos(theta_r) * kelvin_distance

    # y pos of follow point relative to neighbor ship
    dy_l = math.sin(theta_l) * kelvin_distance
    dy_r = math.sin(theta_r) * kelvin_distance

    if surface is not None:
        pygame.draw.line(surface, "blue", (closest_neighbor.x, closest_neighbor.y), (closest_neighbor.x + dx_l, closest_neighbor.y + dy_l))
        pygame.draw.line(surface, "green", (closest_neighbor.x, closest_neighbor.y), (closest_neighbor.x + dx_r, closest_neighbor.y + dy_r))

    # left follow point (relative to neighbor)
    x_l = closest_neighbor.x + dx_l
    y_l = closest_neighbor.y + dy_l

    # right follow point (relative to neighbor)
    x_r = closest_neighbor.x + dx_r
    y_r = closest_neighbor.y + dy_r

    # Distances to follow points
    dl = distance((ship.x, ship.y), (x_l, y_l))
    dr = distance((ship.x, ship.y), (x_r, y_r))

    # Closest follow point
    x, y = 0,0
    if dl < dr:
        x, y =  x_l, y_l
    else:
        x, y =  x_r, y_r

    if surface is not None:
        pygame.draw.circle(surface, "yellow", (x, y), 5)

    return x, y
