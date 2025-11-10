import math

# Math utility functions for maritime simulation
# These functions are performance-critical and can be profiled with tools like py-spy

def vector_dot_product(v1, v2):
    """Calculate dot product of two 2D vectors.
    
    Returns:
        Same direction: positive
        Opposite direction: negative
        Orthogonal: zero
    """
    return v1[0] * v2[0] + v1[1] * v2[1]

def distance(point_a, point_b):
    """Calculate Euclidean distance between two points."""
    ax, ay = point_a
    bx, by = point_b
    return math.sqrt((bx - ax) ** 2 + (by - ay) ** 2)

def magnitude(v):
    """Calculate the magnitude (length) of a 2D vector."""
    return math.sqrt(v[0] * v[0] + v[1] * v[1])

def normalize(v):
    """Normalize a 2D vector to unit length.
    
    Returns the normalized vector, or (0, 0) if magnitude is zero.
    """
    mag = magnitude(v)
    if mag == 0:
        return 0, 0
    return v[0] / mag, v[1] / mag

def hypot(dx, dy):
    """Calculate the Euclidean distance using dx and dy components.
    
    This is equivalent to math.hypot but provides a consistent interface
    with other math utilities in this module.
    """
    return math.hypot(dx, dy)
