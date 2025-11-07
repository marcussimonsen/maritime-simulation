import math
import numpy as np
from pyswarms.single import GlobalBestPSO
from spawn_utils import point_on_land, segment_intersects_any_polygon


def build_adjacency(nodes, polygons, R, ports,
                    alpha_water=1.0, alpha_highway=0.6, beta_switch=200.0):
    """
    Build a 2-layer graph:
      - layer W (open water): index 0..N-1
      - layer H (highway):    index N..2N-1
    Switch edges connect i(W) <-> i(H) with cost beta_switch.
    """
    N = len(nodes)
    adjacency_list = [[] for _ in range(2*N)]

    def add(u, v, cost):
        adjacency_list[u].append((v, cost))
        adjacency_list[v].append((u, cost))

    for i in range(N):
        for j in range(i+1, N):
            x1, y1 = nodes[i]
            x2, y2 = nodes[j]
            dx, dy = x1 - x2, y1 - y2
            d = math.hypot(dx, dy)  # Euclidean distance
            if d <= R and not segment_intersects_any_polygon((x1, y1), (x2, y2), polygons):
                add(i, j, alpha_water * d)  # W -> W

                i_is_h = (i >= ports)
                j_is_h = (j >= ports)
                if i_is_h and j_is_h:  # ports not allowed on highway layer
                    add(N + i, N + j, alpha_highway * d)  # H -> H

    # Mode-switch (enter/exit highway)
    for i in range(N):
        add(i, N + i, beta_switch)

    return adjacency_list  # size 2N


def dijkstra(adj, src, dst):
    import heapq
    n = len(adj)
    dist = [float('inf')]*n
    dist[src] = 0.0
    pq = [(0.0, src)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        if u == dst:
            return d
        for v, w in adj[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(pq, (nd, v))
    return float('inf')


def objective_factory(ports_xy, orders, coastlines, bbox_min, bbox_max, M, R, big_penalty):
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
            adj = build_adjacency(nodes.tolist(), coastlines, R, ports, beta_switch=0.0, alpha_highway=0.1)

            routing_cost = 0.0
            for (origin_index, destination_index, weight) in orders:
                shortest_path = dijkstra(adj, origin_index, destination_index)
                if math.isinf(shortest_path):
                    routing_cost += big_penalty
                else:
                    routing_cost += weight * shortest_path

            costs[k] = routing_cost + penalty
        return costs
    return objective


def optimize_highways(ports_xy, orders, coastlines, bbox_min, bbox_max,
                      M=6, R=250.0, iters=120, particles=60,
                      c1=1.4, c2=1.6, w=0.7, big_penalty=1e7):
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

    cost_function = objective_factory(ports_xy, orders, coastlines, bbox_min, bbox_max, M, R, big_penalty)

    optimizer = GlobalBestPSO(
        n_particles=particles,
        dimensions=dimensions,
        options={'c1': c1, 'c2': c2, 'w': w},
        bounds=bounds
    )
    verbose = True
    best_cost, best_pos = optimizer.optimize(cost_function, iters=iters, verbose=verbose)
    highway_nodes = best_pos.reshape(M, 2)

    # Build final graph (ports + highways) and edges for drawing
    all_nodes = np.vstack([np.array(ports_xy), highway_nodes])
    adjacency_list = build_adjacency(all_nodes.tolist(), coastlines, R)

    edges = []
    for u, neighbors in enumerate(adjacency_list):
        for v, weight in neighbors:
            if u < v:  # to avoid duplicates
                edges.append((u, v))

    return highway_nodes, edges, best_cost, all_nodes
