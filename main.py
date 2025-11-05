import random

import pygame
from coastlines.svg_parser import svg_to_points
from order_utils import add_random_orders
from port import Port
from ship import Ship
from order import Order
from spawn_utils import spawn_not_in_coastlines
from route import draw_route, draw_graph, create_ocean_graph, get_port_route
from ship_manager import ShipManager


SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
route = [(100, 350), (150, 350), (350, 250), (450, 500), (650, 500), (700, 300), (800, 300), (1000, 300), (1200, 300)]


def get_distance(p1, p2):
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5


def get_closest_coastpoint(coastlines):
    x, y = pygame.mouse.get_pos()
    closest_point = (0, 0)
    min_dist = float('inf')
    for coastline in coastlines:
        for point in coastline:
            dist = get_distance((x, y), point)
            if dist < min_dist:
                min_dist = dist
                closest_point = point
    return closest_point


def generate_routes(ports, graph, weights):
    routes = {}
    for i in range(len(ports)):
        for j in range(i + 1, len(ports)):
            a, b = ports[i], ports[j]
            route = [(a.x, a.y)] + get_port_route(a, b, graph, weights) + [(b.x, b.y)]
            routes[(b, a)] = route  # Store as reversed routes because of ship logic
            routes[(a, b)] = route[::-1]
    return routes


def main():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    running = True

    should_add_random_orders = False
    departure_port = None
    destination_port = None
    has_order_color = "green"
    no_order_color = "red"
    container_amount = 0
    show_graph = True
    dt = 0
    creating_order = False
    ship_manager = ShipManager((SCREEN_WIDTH, SCREEN_HEIGHT), screen)

    port_mode = False
    capacities = [10, 20, 30]
    capacity_index = 0

    coastlines = svg_to_points('coastlines/svg/islands.svg', step=40, scale=1.2)

    ports = []
    graph, weights = create_ocean_graph(coastlines, SCREEN_WIDTH, SCREEN_HEIGHT, screen, grid_gap=20, min_dist=20)
    routes = generate_routes(ports, graph, weights)

    ship_manager.spawn_random_ships(coastlines)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if creating_order:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        creating_order = False
                        departure_port.color = no_order_color
                        departure_port = None
                    elif event.key == pygame.K_UP:
                        container_amount += 1
                    elif event.key == pygame.K_DOWN:
                        container_amount = max(0, container_amount - 1)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    for port in ports:
                        dist = get_distance((mouse_x, mouse_y), (port.x, port.y))
                        if dist <= port.radius and port != departure_port:
                            destination_port = port
                            num_containers = container_amount
                            departure_port.add_order(Order(destination_port, num_containers))
                            destination_port.color = has_order_color
                            creating_order = False
                            break
                    continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_p:
                    port_mode = not port_mode
                if event.key == pygame.K_d:
                    ship_manager.toggle_ship_sensors()
                    show_graph = not show_graph
                if event.key == pygame.K_g:
                    routes = generate_routes(ports, graph, weights)
                if event.key == pygame.K_UP:
                    capacity_index = (capacity_index + 1) % len(capacities)
                if event.key == pygame.K_DOWN:
                    capacity_index = (capacity_index-1) % len(capacities)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if port_mode:
                    closest_coastpoint = get_closest_coastpoint(coastlines)
                    port = Port(closest_coastpoint[0], closest_coastpoint[1], capacities[capacity_index], radius=10)
                    for _ in range(5):
                        ship = Ship(port.x, port.y)
                        ship_manager.dock_ship(port, ship)
                    ports.append(port)
                else:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    for port in ports:
                        dist = get_distance((mouse_x, mouse_y), (port.x, port.y))
                        if dist <= port.radius:
                            creating_order = True
                            departure_port = port
                            departure_port.color = "green"
                            break

        screen.fill((0, 105, 148))

        for c in coastlines:
            pygame.draw.polygon(screen, (228, 200, 148), c)

        for r in routes.values():
            draw_route(screen, r)

        ship_manager.update_ships(coastlines)
        ship_manager.update_ports(ports, routes)

        if port_mode:
            point = get_closest_coastpoint(coastlines)
            radius = capacities[capacity_index]

            circle_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
            pygame.draw.circle(circle_surf, (255, 0, 0, 128), (radius, radius), radius)
            pygame.draw.line(screen, (255, 0, 0, 0.5), pygame.mouse.get_pos(), point)
            screen.blit(circle_surf, (point[0] - radius, point[1] - radius))

        if creating_order:
            font = pygame.font.SysFont(None, 36)
            text = font.render(f"{container_amount} container(s)", True, (255, 255, 255))
            screen.blit(text, ((SCREEN_WIDTH // 2) - text.get_width(), (SCREEN_HEIGHT // 2) - text.get_height()))

        if show_graph:
            draw_graph(graph, screen)

        pygame.display.flip()
        dt = clock.tick(60) / 1000  # limits FPS, dt is time since last frame
    pygame.quit()


if __name__ == "__main__":
    main()
