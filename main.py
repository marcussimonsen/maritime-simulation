import random

import pygame

from coastlines.svg_parser import svg_to_points
from port import Port
from ship import Ship
from spawn_utils import spawn_not_in_coastlines
from route import draw_route, draw_graph, create_ocean_graph, get_port_route

SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
route = [(100,350), (150,350), (350, 250), (450, 500), (650, 500), (700, 300), (800, 300), (1000, 300), (1200, 300)]

def get_closest_coastpoint(coastlines):
    x, y = pygame.mouse.get_pos()
    closest_point = (0,0)
    min_dist = float('inf')
    for coastline in coastlines:
        for point in coastline:
            dist = ((point[0] - x) ** 2 + (point[1] - y) ** 2) ** 0.5
            if dist < min_dist:
                min_dist = dist
                closest_point = point
    return closest_point

def main():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    running = True
    show_ship_sensors = True
    dt = 0

    port_mode = False
    capacities = [10, 20, 30]
    capacity_index = 0

    coastlines = svg_to_points('coastlines/svg/islands.svg', step=40, scale=1.2)

    ports = []
    for polygon in coastlines:
        for _ in range(2):
            x, y = random.choice(polygon)
            ports.append(Port(x, y, 10))

    graph, weights = create_ocean_graph(coastlines, SCREEN_WIDTH, SCREEN_HEIGHT, screen, 20)
    route = get_port_route(ports[0], ports[2], graph, weights)

    ships = []
    for _ in range(20):
        x, y = spawn_not_in_coastlines(coastlines, 1280, 720, margin=50, max_attempts=2000)
        ships.append(Ship(x, y, route.copy()))

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_p:
                    port_mode = not port_mode
                if event.key == pygame.K_d:
                    show_ship_sensors = not show_ship_sensors
                if event.key == pygame.K_UP:
                    capacity_index = (capacity_index + 1) % len(capacities)
                if event.key == pygame.K_DOWN:
                    capacity_index = (capacity_index-1) % len(capacities)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if port_mode:
                    closest_coastpoint = get_closest_coastpoint(coastlines)
                    ports.append(Port(closest_coastpoint[0], closest_coastpoint[1], capacities[capacity_index], radius=capacities[capacity_index]))

        screen.fill((0, 105, 148))

        for c in coastlines:
            pygame.draw.polygon(screen, (228, 200, 148), c)

        draw_route(screen, route)

        for ship in ships:
            ship.boundary_update(1280, 720)
            ship.flocking(ships)
            ship.follow_route(surface=screen if show_ship_sensors else None)
            ship.move(ships, coastlines, surface=screen if show_ship_sensors else None)
            ship.draw(screen)

        for port in ports:
            port.dock_nearby_ships(ships)
            port.draw(screen)

        if port_mode:
            point = get_closest_coastpoint(coastlines)
            radius = capacities[capacity_index]

            circle_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)   
            pygame.draw.circle(circle_surf, (255, 0, 0, 128), (radius, radius), radius)
            pygame.draw.line(screen, (255, 0, 0, 0.5), pygame.mouse.get_pos(), point)
            screen.blit(circle_surf, (point[0] - radius, point[1] - radius))

        draw_graph(graph, screen)

        pygame.display.flip()
        dt = clock.tick(60) / 1000 # limits FPS, dt is time since last frame
    pygame.quit()

if __name__ == "__main__":
    main()
