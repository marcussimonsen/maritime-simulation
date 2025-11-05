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

def kelvin_cohesion(ship, neighbors):
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

def find_optimal_sailing_points(ship, distance_to_boat_ahead):
    pass
