import pygame
import random
from typing import List, Tuple

Point = Tuple[int, int]
Polygon = List[Point]

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

def spawn_not_in_coastlines(coastlines, w, h, margin=0, max_attempts=1000):
    """Return a random (x,y) not inside any coastline. Falls back to center if none found."""
    for _ in range(max_attempts):
        x = random.randint(margin, w - margin)
        y = random.randint(margin, h - margin)
        if not any(point_in_polygon((x, y), poly) for poly in coastlines):
            return x, y
    # fallback: return map center (deterministic, safer than an arbitrary hardcoded point)
    print("Warning: spawn_not_in_coastlines failed to find free spot — using map center fallback")
    return w // 2, h // 2
