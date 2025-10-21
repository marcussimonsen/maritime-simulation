import pygame
from ship import *
from coastlines.svg_parser import svg_to_points


def main():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()
    running = True
    dt = 0

    coastlines = svg_to_points('coastlines/svg/islands.svg', step=40, scale=1.2)

    ships = []
    for _ in range(10):
        ships.append(Ship(random.randint(100, 1000), random.randint(100, 600)))

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 105, 148))

        for c in coastlines:
            pygame.draw.polygon(screen, (228, 200, 148), c)

        for ship in ships:
            ship.boundary_update(1280, 720)
            ship.move(ships, coastlines, screen)

        for ship in ships:
            ship.draw(screen)

        # Render stuff here

        pygame.display.flip()
        dt = clock.tick(60) / 1000 # limits FPS and
    pygame.quit()

if __name__ == "__main__":
    main()
