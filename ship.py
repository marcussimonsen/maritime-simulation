import numpy as np
import pygame


def line_from_points(p1, p2):
    a = (p2[1] - p1[1]) / (p2[0] - p1[0])
    b = p1[1] - a * p1[0]
    return a, b

def intersection_point(line1, line2):
    # Each line is given as (a, b, c) where ax + by = c
    a1, b1, c1 = line1
    a2, b2, c2 = line2

    determinant = a1 * b2 - a2 * b1

    if determinant == 0:
        return None  # Lines are parallel or coincident

    x = (c1 * b2 - c2 * b1) / determinant
    y = (a1 * c2 - a2 * c1) / determinant
    return (x, y)


class Ship:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 1
        self.vy = 1

        self.rect = pygame.Rect(self.x, self.y, 10, 20)

    def draw(self, surface):
        pygame.draw.rect(surface, "black", self.rect)

    def move(self, ships, coastlines):
        b_line = line_from_points((self.x, self.y), (self.x + self.vx, self.y + self.vy))
        for coastline in coastlines:
            for p1, p2 in zip(coastline, coastline[1:]):
                c_line = line_from_points(p1, p2)



