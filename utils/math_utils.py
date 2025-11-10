import math
import random
import pygame

EPS = 1e-9

def get_distance(p1, p2):
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5

def vector_dot_product(v1, v2):
    # Same direction: positive
    # Opposite direction: negtive
    # Orthogonal: zero
    return v1[0] * v2[0] + v1[1] * v2[1]


def distance(point_a, point_b):
    ax, ay = point_a
    bx, by = point_b
    return math.sqrt((bx - ax) ** 2 + (by - ay) ** 2)


def magnitude(v):
    return math.sqrt(v[0] * v[0] + v[1] * v[1])


def point_in_polygon(point, poly):
    x, y = point
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        intersect = ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi)
        if intersect:
            inside = not inside
        j = i
    return inside

def get_closest_coastpoint(coastlines):
    x, y = pygame.mouse.get_pos()
    closest_point = (0, 0)
    min_dist = float('inf')
    for coastline in coastlines:
        for point in coastline:
            dist = distance((x, y), point)
            if dist < min_dist:
                min_dist = dist
                closest_point = point
    return closest_point

def point_on_land(pt, polygons):
    return any(point_in_polygon(pt, poly) for poly in polygons)


def on_segment(a, b, c, eps=EPS):
    return (min(a[0], b[0]) - 1e-9 <= c[0] <= max(a[0], b[0]) + EPS and
            min(a[1], b[1]) - 1e-9 <= c[1] <= max(a[1], b[1]) + EPS)


def orient(a, b, c):
    return (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0])


def segments_intersect(p1, p2, q1, q2, eps=EPS):
    o1 = orient(p1, p2, q1)
    o2 = orient(p1, p2, q2)
    o3 = orient(q1, q2, p1)
    o4 = orient(q1, q2, p2)

    if abs(o1) < eps and on_segment(p1, p2, q1):
        return False
    if abs(o2) < eps and on_segment(p1, p2, q2):
        return False
    if abs(o3) < eps and on_segment(q1, q2, p1):
        return False
    if abs(o4) < eps and on_segment(q1, q2, p2):
        return False

    return (o1 * o2 < -eps) and (o3 * o4 < -eps)


def segment_intersects_any_polygon(p, q, polygons):
    for poly in polygons:
        n = len(poly)
        for i in range(n):
            a = poly[i]
            b = poly[(i+1) % n]
            if segments_intersect(p, q, a, b):
                return True
    return False

