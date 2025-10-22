import pygame
from ship import *
from coastlines.svg_parser import svg_to_points
import random
from spawn_utils import spawn_not_in_coastlines, build_occupancy_grid, spawn_from_free_cells


def main():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()
    running = True
    dt = 0

    coastlines = svg_to_points('coastlines/svg/islands.svg', step=40, scale=1.2)


    # Option A: use point-in-polygon sampler
    ships = []
    for _ in range(10):
        x, y = spawn_not_in_coastlines(coastlines, 1280, 720, margin=50, max_attempts=2000)
        ships.append(Ship(x, y))

    # Option B: build occupancy grid once and sample free cells (faster if many spawns)
    # Build occupancy + mask
    # free_cells, cell_size, coastline_mask = build_occupancy_grid(coastlines, 1280, 720, cell_size=8)

    # ships = []
    # for _ in range(10):
    #     # pass ship_radius (clearance). Tune to ship size.
    #     x, y = spawn_from_free_cells(free_cells, cell_size, 1280, 720,
    #                                  coastline_mask=coastline_mask, ship_radius=12, max_attempts=500)
    #     ships.append(Ship(x, y))


    # Random spawn
    # ships = []
    # for _ in range(10):
    #     ships.append(Ship(random.randint(100, 1000), random.randint(100, 600)))

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
