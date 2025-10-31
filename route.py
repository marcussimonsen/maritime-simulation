import pygame

def draw_route(surface, route):
    for a,b in zip(route, route[1:]):
        pygame.draw.line(surface, "red", a, b)

def find_velocity(route, ship_position):
    #route - pos
    rx, ry = route[-1]
    sx, sy = ship_position

    return rx - sx, ry - sy