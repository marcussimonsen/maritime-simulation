import heapq
from collections import defaultdict
from math import dist, inf

import numpy as np
import pygame

from port import Port
from spawn_utils import point_in_polygon


def close_to_coastline(point, coastlines, min_dist):
    for poly in coastlines:
        for p in poly:
            if dist(point, p) < min_dist:
                return True
    return False

def get_closest_point(p, lst):
    min_dist = None
    closest_point = None
    for p2 in lst:
        d = dist(p, p2)
        if min_dist is None or d < min_dist:
            min_dist = d
            closest_point = p2
    return closest_point

def get_port_route(port_a: Port, port_b: Port, graph, weight):
    a = get_closest_point((port_a.x, port_a.y), graph.keys())
    b = get_closest_point((port_b.x, port_b.y), graph.keys())
    return dijkstra(graph, weight, a, b)[-1]


def create_ocean_graph(coastlines, screen_width, screen_height, screen, grid_gap, min_dist):
    graph = defaultdict(list)
    weight = {}
    for x in range(0 + grid_gap, screen_width, grid_gap):
        for y in range(0 + grid_gap, screen_height, grid_gap):
            if not any([point_in_polygon((x, y), poly) or close_to_coastline((x, y), coastlines, min_dist) for poly in coastlines]):
                graph[(x, y)] = []

    for x, y in graph.keys():
        for x2, y2 in [(x - grid_gap, y),
                       (x + grid_gap, y),
                       (x, y - grid_gap),
                       (x, y + grid_gap),
                       (x - grid_gap, y - grid_gap),
                       (x - grid_gap, y + grid_gap),
                       (x + grid_gap, y + grid_gap),
                       (x + grid_gap, y - grid_gap)]:
            if (x2, y2) in graph.keys():
                graph[(x, y)].append((x2, y2))
                if x == x2 or y == y2:
                    weight[(x, y), (x2, y2)] = grid_gap
                else:
                    weight[(x, y), (x2, y2)] = np.sqrt(grid_gap ** 2 + grid_gap ** 2)
        for x2, y2 in [(x - 2*grid_gap, y - grid_gap),
                       (x - 2*grid_gap, y + grid_gap),
                       (x + 2*grid_gap, y - grid_gap),
                       (x + 2*grid_gap, y + grid_gap),
                       (x - grid_gap, y - 2*grid_gap),
                       (x + grid_gap, y - 2*grid_gap),
                       (x - grid_gap, y + 2*grid_gap),
                       (x + grid_gap, y + 2*grid_gap)]:
            if (x2, y2) in graph.keys():
                graph[(x, y)].append((x2, y2))
                weight[(x, y), (x2, y2)] = np.sqrt((grid_gap*2) **2 + grid_gap ** 2)


    return graph, weight

def draw_graph(graph: dict, screen):
    for point in graph.keys():
        pygame.draw.circle(screen, (0,0,0), point, 1)

def draw_route(surface, route):
    for a,b in zip(route, route[1:]):
        pygame.draw.line(surface, "red", a, b)

def find_velocity(route, ship_position):
    #route - pos
    rx, ry = route[-1]
    sx, sy = ship_position

    return rx - sx, ry - sy


def dijkstra(graph, weight, s, t):
    """
    `graph`: an adjacency list (defaultdict(list))
    `weight`: a dictionary where weight[(v, w)] is weight of the edge v -> w
    """

    pq = []
    distances = defaultdict(lambda: inf)
    distances[s] = 0
    heapq.heappush(pq, (0, s))
    edge_to = defaultdict(lambda: None)

    while pq:
        current_dist, node = heapq.heappop(pq)

        if node == t:

            # Construct path
            path = []
            while node:
                path.append(node)
                node = edge_to[node]
            return current_dist, path[::-1]

        if current_dist > distances[node]:
            continue

        # Update distances for neighbors
        for neighbor in graph[node]:
            if (node, neighbor) not in weight:
                print(f"Error: Missing weight for edge {node} -> {neighbor}")
                continue
            neighbor_dist = current_dist + weight[(node, neighbor)]

            if neighbor_dist < distances[neighbor]:
                distances[neighbor] = neighbor_dist
                edge_to[neighbor] = node
                heapq.heappush(pq, (neighbor_dist, neighbor))

    return None, []
