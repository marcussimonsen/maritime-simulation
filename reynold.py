def alignment(ship, neighbors) -> (float, float):
    avg_velx = 0
    avg_vely = 0

    for other in neighbors:
        avg_velx += other.vx
        avg_vely += other.vy

    if len(neighbors) > 0:
        avg_velx /= len(neighbors)
        avg_vely /= len(neighbors)

    return avg_velx, avg_vely


def separation(ship, neighbors) -> (float, float):
    x = 0
    y = 0

    for other in neighbors:
        x +=  (ship.x - other.x + 1e-12)
        y +=  (ship.y - other.y + 1e-12)

    return x, y

def cohesion(ship, neighbors) -> (float, float):
    avg_posx = 0
    avg_posy = 0

    for other in neighbors:
        avg_posx += other.x
        avg_posy += other.y

    if len(neighbors) > 0:
        avg_posx /= len(neighbors)
        avg_posy /= len(neighbors)

    return avg_posx, avg_posy
