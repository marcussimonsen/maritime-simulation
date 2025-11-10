import math
import heapq
import numpy as np
from pyswarms.single import GlobalBestPSO
from spawn_utils import point_on_land, segment_intersects_any_polygon
from collections import defaultdict
from math import inf
from utils import hypot


def layered_index_base(idx, N):
    return idx if idx < N else idx - N


def path_indices_to_xy(path_idxs, all_nodes):
    N = len(all_nodes)
    coords = []
    for idx in path_idxs:
        base = layered_index_base(idx, N)
        coords.append(tuple(all_nodes[base]))
    return coords


def build_adjacency_layered(nodes, polygons, R, ports,
                            alpha_water=1.0, alpha_highway=0.6, beta_switch=200.0):
    """
    Build a 2-layer graph:
      - layer W (open water): index 0..N-1
      - layer H (highway):    index N..2N-1
    Switch edges connect i(W) <-> i(H) with cost beta_switch.
    """
    N = len(nodes)
    adjacency_list = [[] for _ in range(2*N)]
    weights = {}

    def add(u, v, cost):
        adjacency_list[u].append(v)
        weights[(u, v)] = cost
        adjacency_list[v].append(u)
        weights[(v, u)] = cost

    for i in range(N):
        for j in range(i+1, N):
            x1, y1 = nodes[i]
            x2, y2 = nodes[j]
            dx, dy = x1 - x2, y1 - y2
            d = hypot(dx, dy)  # Euclidean distance
            if d <= R and not segment_intersects_any_polygon((x1, y1), (x2, y2), polygons):
                add(i, j, alpha_water * d)  # W -> W

                i_is_h = (i >= ports)
                j_is_h = (j >= ports)
                if i_is_h and j_is_h:  # ports not allowed on highway layer
                    add(N + i, N + j, alpha_highway * d)  # H -> H

    # Mode-switch (enter/exit highway)
    for i in range(N):
        add(i, N + i, beta_switch)

    return adjacency_list, weights  # size 2N


def build_adjacency(nodes, polygons, radius):
    n = len(nodes)
    adj = [[] for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            dx = nodes[i][0] - nodes[j][0]
            dy = nodes[i][1] - nodes[j][1]
            d = hypot(dx, dy)
            if d <= radius and not segment_intersects_any_polygon(nodes[i], nodes[j], polygons):
                adj[i].append((j, d))
                adj[j].append((i, d))
    return adj


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
            while node is not None:
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


def objective_factory(ports_xy, orders, coastlines, bbox_min, bbox_max, M, R, big_penalty, alpha_water, alpha_highway, beta_switch):
    '''
    Create cost function for PSO.
    Args:
        R: connection radius
        M: number of highway nodes
    '''

    ports_xy = np.array(ports_xy)  # shape (P,2)
    ports = ports_xy.shape[0]

    def objective(X):
        # X shape: (n_particles, 2*M)

        costs = np.zeros(X.shape[0], dtype=float)  # cost value for each particle

        for k in range(X.shape[0]):
            highway_points = X[k].reshape(M, 2)

            # Bound check + on-land check
            is_out_of_bounds = np.any((highway_points < bbox_min) | (highway_points > bbox_max), axis=1)
            onland = np.array([point_on_land(tuple(point), coastlines) for point in highway_points])
            penalty = (is_out_of_bounds | onland).sum() * big_penalty

            nodes = np.vstack([ports_xy, highway_points])  # all nodes

            # Graph building handles isolated nodes
            adj, weights = build_adjacency_layered(nodes.tolist(), coastlines, R, ports, alpha_water, alpha_highway, beta_switch)

            routing_cost = 0.0
            for (origin_index, destination_index, weight) in orders:
                shortest_path, _ = dijkstra(adj, weights, origin_index, destination_index)
                if math.isinf(shortest_path):
                    routing_cost += big_penalty
                else:
                    routing_cost += weight * shortest_path

            costs[k] = routing_cost + penalty
        return costs
    return objective


def optimize_highways(ports_xy, orders, coastlines, bbox_min, bbox_max,
                      M=6, R=250.0, iters=120, particles=60,
                      c1=1.4, c2=1.6, w=0.7, big_penalty=1e7,
                      alpha_water=1.0, alpha_highway=0.6, beta_switch=200.0):
    """
    Optiomize highway node positions using particle swarm optimization.

    Args:
        M: number of highway nodes
        R: connection radius
        ports_xy: list[(x,y)]
        orders: list[(origin_port_idx, dest_port_idx, weight)]
        bbox_min/bbox_max: np.array([minx,miny]), np.array([maxx,maxy])
    """
    dimensions = 2*M

    # below is because each highway node has seperate bounds (although they are the same)
    lower = np.tile(bbox_min, M)
    upper = np.tile(bbox_max, M)
    bounds = (lower, upper)

    cost_function = objective_factory(ports_xy, orders, coastlines, bbox_min, bbox_max, M, R, big_penalty, alpha_water, alpha_highway, beta_switch)

    optimizer = GlobalBestPSO(
        n_particles=particles,
        dimensions=dimensions,
        options={'c1': c1, 'c2': c2, 'w': w},
        bounds=bounds
    )
    verbose = True
    best_cost, best_pos = optimizer.optimize(cost_function, iters=iters, verbose=verbose)
    highway_nodes = best_pos.reshape(M, 2)

    all_nodes = np.vstack([np.array(ports_xy), highway_nodes])
    P = len(ports_xy)

    adj_layered, weights = build_adjacency_layered(all_nodes.tolist(), coastlines, R, P, alpha_water, alpha_highway, beta_switch)

    # single-layer adjacencies (all nodes (the white ones))
    adjacency_list_single = build_adjacency(all_nodes.tolist(), coastlines, R)
    edges = []
    for u, neighbors in enumerate(adjacency_list_single):
        for v, weight in neighbors:
            if u < v:
                edges.append((u, v))

    # Shortest path for each order
    order_paths_xy = []
    for (origin_idx, dest_idx, w) in orders:
        dist, path = dijkstra(adj_layered, weights, origin_idx, dest_idx)
        order_paths_xy.append(path_indices_to_xy(path, all_nodes))

    return highway_nodes, edges, best_cost, all_nodes, order_paths_xy
