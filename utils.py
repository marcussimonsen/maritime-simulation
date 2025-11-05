import math

# TODO: move math methods in here!

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
