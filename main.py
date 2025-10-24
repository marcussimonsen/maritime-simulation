import pygame
from ship import *
from port import *
from coastlines.svg_parser import svg_to_points
import random
from types import SimpleNamespace
from spawn_utils import spawn_not_in_coastlines, build_occupancy_grid, spawn_from_free_cells


def main():
    pygame.init()
    screen_width, screen_height = 1280, 720
    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()
    running = True
    dt = 0

    port_mode = False
    capacities = [10, 20, 30]
    capacity_index = 0

    show_info_box = True

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

    ports = []
    for polygon in coastlines:
        for _ in range(2):
            x, y = random.choice(polygon)
            ports.append(Port(x, y, 10))

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_p:
                    port_mode = not port_mode
                if event.key == pygame.K_UP:
                    capacity_index = (capacity_index + 1) % len(capacities)
                if event.key == pygame.K_DOWN:
                    if capacity_index == 0:
                        capacity_index = len(capacities) - 1
                        print(capacity_index)
                    else:
                        capacity_index = capacity_index - 1

            if event.type == pygame.MOUSEBUTTONDOWN and port_mode:
                x, y = pygame.mouse.get_pos()
                closest_point = (0,0)
                min_dist = float('inf')
                for coastline in coastlines:
                    for point in coastline:
                        dist = ((point[0] - x) ** 2 + (point[1] - y) ** 2) ** 0.5
                        if dist < min_dist:
                            min_dist = dist
                            closest_point = point
                ports.append(Port(closest_point[0], closest_point[1], capacities[capacity_index]))
                

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

        if show_info_box:
            box_width, box_height = 250, 100
            info_box = pygame.Surface((box_width, box_height))
            info_box.set_alpha(200)
            info_box.fill((50, 50, 50))
            screen.blit(info_box, (screen_width - box_width - 10, 10))

            font = pygame.font.SysFont(None, 24)
            mode_text = "Port Mode: ON" if port_mode else "Port Mode: OFF"
            mode_surface = font.render(mode_text, True, (255, 255, 255))
            screen.blit(mode_surface, (screen_width - box_width, 20))

            capacity_text = f"Port Capacity: {capacities[capacity_index]}"
            capacity_surface = font.render(capacity_text, True, (255, 255, 255))
            screen.blit(capacity_surface, (screen_width - box_width, 50))


        pygame.display.flip()
        dt = clock.tick(60) / 1000 # limits FPS and
    pygame.quit()

if __name__ == "__main__":
    main()
