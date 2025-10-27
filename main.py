import random

import pygame

from coastlines.svg_parser import svg_to_points
from ship import Ship
from spawn_utils import spawn_not_in_coastlines


def main():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()
    running = True
    dt = 0

    coastlines = svg_to_points('coastlines/svg/islands.svg', step=40, scale=1.2)

    ships = []
    for _ in range(10):
        x, y = spawn_not_in_coastlines(coastlines, 1280, 720, margin=50, max_attempts=2000)
        ships.append(Ship(x, y))

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 105, 148))

        for c in coastlines:
            pygame.draw.polygon(screen, (228, 200, 148), c)

        for ship in ships:
            ship.boundary_update(1280, 720)
            ship.move(ships, coastlines, surface=screen)

        for ship in ships:
            ship.draw(screen)

        # Render stuff here

        pygame.display.flip()
        dt = clock.tick(60) / 1000 # limits FPS and
    pygame.quit()

if __name__ == "__main__":
    main()
