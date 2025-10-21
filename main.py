import pygame
from ship import *
from coastlines.svg_parser import svg_to_points


def main():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()
    running = True
    dt = 0

    coastlines = svg_to_points('coastlines/svg/test.svg', step=1, scale=0.7)

    ships = [Ship(300, 300)]

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 105, 148))

        for c in coastlines:
            pygame.draw.polygon(screen, (228, 200, 148), c)

        for ship in ships:
            ship.draw(screen)

        # Render stuff here

        pygame.display.flip()
        dt = clock.tick(60) / 1000 # limits FPS and
    pygame.quit()

if __name__ == "__main__":
    main()
