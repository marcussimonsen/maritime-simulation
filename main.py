import pygame
from ship import *
from port import *
from coastlines.svg_parser import svg_to_points
import random


def main():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()
    running = True
    dt = 0

    coastlines = svg_to_points('coastlines/svg/islands.svg', step=40, scale=1.2)
    print(coastlines[0])

    ships = []
    for _ in range(10):
        ships.append(Ship(random.randint(100, 1000), random.randint(100, 600)))

    ports = []
    for polygon in coastlines:
        for _ in range(2):
            x, y = random.choice(polygon)
            ports.append(Port(x, y, 10))

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

        for port in ports:
            port.draw(screen)

        # Render stuff here

        pygame.display.flip()
        dt = clock.tick(60) / 1000 # limits FPS and
    pygame.quit()

if __name__ == "__main__":
    main()
