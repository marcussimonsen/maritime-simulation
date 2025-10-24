import pygame
import random
from typing import List, Tuple

Point = Tuple[int, int]
Polygon = List[Point]


### Option A – point-in-polygon test ###
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



### Option B – occupancy grid rasterization ###
# cache circle masks by radius to avoid rebuilding
_circle_mask_cache = {}

def _make_circle_mask(radius: int) -> "pygame.Mask":
    """Return a pygame.Mask with a filled circle of given radius."""
    if radius in _circle_mask_cache:
        return _circle_mask_cache[radius]
    d = radius * 2 + 1
    surf = pygame.Surface((d, d), flags=pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    pygame.draw.circle(surf, (255, 255, 255, 255), (radius, radius), radius)
    mask = pygame.mask.from_surface(surf)
    _circle_mask_cache[radius] = mask
    return mask

def build_occupancy_grid(coastlines: List[Polygon], width: int, height: int,
                         cell_size: int = 8):
    """Rasterize coastlines into a pygame.mask and return list of free cells (c,r),
    the cell_size, and the coastline mask (pygame.Mask)."""
    surface = pygame.Surface((width, height), flags=pygame.SRCALPHA)
    surface.fill((0, 0, 0, 0))
    for poly in coastlines:
        pygame.draw.polygon(surface, (255, 255, 255, 255), poly)
    coastline_mask = pygame.mask.from_surface(surface)

    cols = (width + cell_size - 1) // cell_size
    rows = (height + cell_size - 1) // cell_size
    free_cells = []
    for r in range(rows):
        for c in range(cols):
            cx = c * cell_size + cell_size // 2
            cy = r * cell_size + cell_size // 2
            if 0 <= cx < width and 0 <= cy < height and coastline_mask.get_at((cx, cy)):
                # blocked if center is on land (coarse test)
                continue
            free_cells.append((c, r))
    return free_cells, cell_size, coastline_mask

def spawn_from_free_cells(free_cells: List[Tuple[int,int]], cell_size: int,
                          width: int, height: int,
                          coastline_mask: "pygame.Mask" = None,
                          ship_radius: int = 0,
                          max_attempts: int = 1000) -> Point:
    """Pick a random free cell and return a random point inside that cell.
    If coastline_mask and ship_radius are provided, verify there is no overlap
    between a circular ship footprint and the coastline before accepting."""
    if not free_cells:
        return width // 2, height // 2

    circle_mask = None
    if coastline_mask is not None and ship_radius > 0:
        circle_mask = _make_circle_mask(ship_radius)

    for _ in range(max_attempts):
        c, r = random.choice(free_cells)
        x = c * cell_size + random.randint(0, cell_size - 1)
        y = r * cell_size + random.randint(0, cell_size - 1)
        x = max(0, min(width - 1, x))
        y = max(0, min(height - 1, y))

        # If no mask checking requested, accept immediately
        if coastline_mask is None or circle_mask is None:
            return x, y

        # Check overlap: circle_mask placed with its topleft at (x - r, y - r)
        offset = (int(x - ship_radius), int(y - ship_radius))
        if coastline_mask.overlap(circle_mask, offset) is None:
            # no overlap -> safe spot
            return x, y
        # else: overlap -> try again

    # fallback: return map center if nothing found
    print("Warning: spawn_from_free_cells failed to find free spot — using map center fallback")
    return width // 2, height // 2
    