import pygame
from ship import *


def main():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()
    running = True
    dt = 0

    coastline = [(0, 0), (200, -30), (180, 50), (100, 100), (120, 200), (110, 300), (170, 500), (100, 600), (90, 800), (0, 720)]

    ships = [Ship(300, 300)]

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 105, 148))

        pygame.draw.polygon(screen, (228, 200, 148), coastline)

        for ship in ships:
            ship.draw(screen)

        # Render stuff here

        pygame.display.flip()
        dt = clock.tick(60) / 1000 # limits FPS and
    pygame.quit()

if __name__ == "__main__":
    main()
