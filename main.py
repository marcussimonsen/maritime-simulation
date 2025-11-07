
import pygame
from coastlines.svg_parser import svg_to_points
from order_utils import add_random_orders
from spawn_utils import spawn_not_in_coastlines
from PSO.highway_optimizer import optimize_highways
from port import Port
from ship import Ship
from order import Order
from route_manager import RouteManager
from ship_manager import ShipManager
import numpy as np
from threading import Event
from queue import Queue
from PSO.optimizer_worker import run_optimizer_task
from threading import Thread


SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720


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


def collect_ports_and_orders(ports):
    '''
    returns pair of:
    ports_xy: List of (x,y) tuples
    orders: List of (origin_index, dest_index, containers)
    '''
    ports_xy = [(port.x, port.y) for port in ports]
    orders = []
    for origin_index, port in enumerate(ports):
        for order in port.orders:
            dest_index = ports.index(order.destination)
            orders.append((origin_index, dest_index, order.containers))

    return ports_xy, orders


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
    route_manager = RouteManager(SCREEN_WIDTH, SCREEN_HEIGHT, screen)
    ship_manager = ShipManager((SCREEN_WIDTH, SCREEN_HEIGHT), screen, route_manager.routes)

    # TODO: Opmtimization state: move from main
    highway_nodes = None
    highway_edges = None
    all_nodes_for_draw = None
    optimizing = False
    optimize_result_queue = Queue()
    optimize_cancel_event = Event()
    optimizer_thread = None

    port_mode = False
    capacities = [10, 20, 30]
    capacity_index = 0

    coastlines = svg_to_points('coastlines/svg/islands.svg', step=40, scale=1.2)

    ports = []
    graph, weights = route_manager.create_ocean_graph(coastlines, screen, grid_gap=20, min_dist=20)

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
                    route_manager.generate_routes(ports, graph, weights)
                if event.key == pygame.K_h:
                    if not optimizing:
                        ports_xy, orders = collect_ports_and_orders(ports)
                        bbox_min = np.array([0.0, 0.0])
                        bbox_max = np.array([SCREEN_WIDTH, SCREEN_HEIGHT])
                        kwargs = dict(
                            ports_xy=ports_xy,
                            orders=orders,
                            coastlines=coastlines,
                            bbox_min=bbox_min,
                            bbox_max=bbox_max,
                            M=4,  # number of highway nodes
                            R=800,  # Radius. TODO: use k-nearest (k = 6) instead
                            iters=150,
                            particles=60,
                            big_penalty=1e7,  # Penalty for disconnected orders
                            c2=1.8

                        )
                        optimize_cancel_event.clear()
                        optimizing = True

                        optimizer_thread = Thread(
                            target=run_optimizer_task,
                            args=(optimize_highways, kwargs, optimize_result_queue, optimize_cancel_event),
                            daemon=True
                        )
                        optimizer_thread.start()
                        print("[Highways] Optimization started...")

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

        route_manager.draw_routes()

        ship_manager.update_ships(coastlines)
        ship_manager.update_ports(ports, route_manager.routes)

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
            route_manager.draw_graph(graph, screen)

        if highway_nodes is not None and all_nodes_for_draw is not None and highway_edges is not None:
            for edge in highway_edges:
                u, v = edge
                start_pos = all_nodes_for_draw[u]
                end_pos = all_nodes_for_draw[v]
                pygame.draw.line(screen, (255, 255, 255), start_pos, end_pos, 3)

            for node in highway_nodes:
                pygame.draw.circle(screen, (255, 255, 255), (int(node[0]), int(node[1])), 5)

        if optimizing:
            font = pygame.font.SysFont(None, 24)
            txt = font.render("Optimizing highways…", True, (255, 255, 255))
            screen.blit(txt, (10, 10))

        # Poll results
        if optimizing:
            try:
                ok, payload = optimize_result_queue.get_nowait()
                optimizing = False
                if ok:
                    highway_nodes, highway_edges, best_cost, all_nodes_for_draw = payload
                    print(f"[Highways] Optimization finished: cost={best_cost:.2f}, nodes={len(highway_nodes)}, edges={len(highway_edges)}")
                else:
                    print(f"[Highways] Optimization failed: {payload}")
            except Exception:
                pass

        pygame.display.flip()
        dt = clock.tick(60) / 1000  # limits FPS, dt is time since last frame
    pygame.quit()


if __name__ == "__main__":
    main()
