import pygame

def draw_route(surface, route):
     for a,b in zip(route, route[1:]):
          pygame.draw.line(surface, "red", a, b)
