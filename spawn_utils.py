import random
from typing import List, Tuple

Point = Tuple[int, int]
Polygon = List[Point]
EPS = 1e-9

# TODO: refactor to geometry_utils.py


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

    # Fast reject for collinear cases
    if abs(o1) < eps and on_segment(p1, p2, q1):  # q1 on p1p2
        # touching (endpoint or along) -> not a proper crossing
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


def spawn_not_in_coastlines(coastlines, w, h, margin=0, max_attempts=1000):
    """Return a random (x,y) not inside any coastline. Falls back to center if none found."""
    for _ in range(max_attempts):
        x = random.randint(margin+1000, w - margin)  # TODO: function take minimum x and y as well
        y = random.randint(margin, h - margin)
        if not any(point_in_polygon((x, y), poly) for poly in coastlines):
            return x, y
    # fallback: return map center (deterministic, safer than an arbitrary hardcoded point)
    print("Warning: spawn_not_in_coastlines failed to find free spot — using map center fallback")
    return w // 2, h // 2
