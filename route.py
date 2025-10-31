import pygame
from collections import defaultdict
from math import inf
import heapq

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


def example():
    graph = defaultdict(list, {
        'A': ['B', 'C'],
        'B': ['D'],
        'C': ['D', 'E'],
        'D': ['E'],
        'E': []
    })

    weight = {
        ('A', 'B'): 1,
        ('A', 'C'): 4,
        ('B', 'D'): 2,
        ('C', 'D'): 5,
        ('C', 'E'): 3,
        ('D', 'E'): 1
    }

    print(dijkstra(graph, weight, 'A', 'E'))  # Output: (6, ['A', 'B', 'D', 'E'])


example()
