import math
import numpy as np
from pyswarms.single import GlobalBestPSO
from spawn_utils import point_on_land, segment_intersects_any_polygon


def build_adjacency(nodes, polygons, radius):
    n = len(nodes)
    adj = [[] for _ in range(n)]
    for i in range(n):
        for j in range(i+1, n):
            dx = nodes[i][0]-nodes[j][0]
            dy = nodes[i][1]-nodes[j][1]
            d = math.hypot(dx, dy)
            if d <= radius and not segment_intersects_any_polygon(nodes[i], nodes[j], polygons):
                adj[i].append((j, d))
                adj[j].append((i, d))
    return adj


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


def objective_factory(ports_xy, orders, coastlines, bbox_min, bbox_max, M, R, big_penalty, spread_lambda=0.0):
    ports_xy = np.array(ports_xy)  # shape (P,2)
    P = ports_xy.shape[0]

    def objective(X):
        # X shape: (n_particles, 2*M)

        costs = np.zeros(X.shape[0], dtype=float)
        for k in range(X.shape[0]):
            vec = X[k].reshape(M, 2)
            # Bound check + on-land check
            oob = np.any((vec < bbox_min) | (vec > bbox_max), axis=1)
            onland = np.array([point_on_land(tuple(pt), coastlines) for pt in vec])
            hard_pen = (oob | onland).sum() * big_penalty

            nodes = np.vstack([ports_xy, vec])  # all nodes
            # If any highway node is isolated by land, graph build will handle it

            # Build adjacency
            adj = build_adjacency(nodes.tolist(), coastlines, R)

            # Routing cost
            routing = 0.0
            for (o, d, w) in orders:
                # o,d are port indices [0..P-1]
                sp = dijkstra(adj, int(o), int(d))
                if math.isinf(sp):
                    routing += big_penalty
                else:
                    routing += w * sp

            # Optional: discourage node overlap (soft spread)
            spread_pen = 0.0
            if spread_lambda > 0.0 and M > 1:
                dmat = np.linalg.norm(vec[:, None, :] - vec[None, :, :], axis=2) + np.eye(M)*1e9
                spread_pen = spread_lambda * np.sum(np.exp(-(dmat/200.0)))  # 200 px scale

            costs[k] = routing + hard_pen + spread_pen
        return costs
    return objective


def optimize_highways(ports_xy, orders, coastlines, bbox_min, bbox_max,
                      M=6, R=250.0, iters=120, particles=60,
                      c1=1.4, c2=1.6, w=0.7, big_penalty=1e7, spread_lambda=0.0):
    """
    Optiomize highway node positions using particle swarm optimization.

    ports_xy: list[(x,y)]
    orders: list[(origin_port_idx, dest_port_idx, weight)]
    coastlines: list of polygons, each polygon is list[(x,y)] in screen coords
    bbox_min/bbox_max: np.array([minx,miny]), np.array([maxx,maxy])
    """
    dim = 2*M
    lower = np.tile(bbox_min, M)
    upper = np.tile(bbox_max, M)
    bounds = (lower, upper)

    obj = objective_factory(ports_xy, orders, coastlines, bbox_min, bbox_max, M, R, big_penalty, spread_lambda)

    optimizer = GlobalBestPSO(
        n_particles=particles,
        dimensions=dim,
        options={'c1': c1, 'c2': c2, 'w': w},
        bounds=bounds
    )
    best_cost, best_pos = optimizer.optimize(obj, iters=iters, verbose=False)
    highway_nodes = best_pos.reshape(M, 2)

    # Build final graph (ports + highways) and edges for drawing
    all_nodes = np.vstack([np.array(ports_xy), highway_nodes])
    adj = build_adjacency(all_nodes.tolist(), coastlines, R)

    edges = []
    for u, nbrs in enumerate(adj):
        for v, w in nbrs:
            if u < v:
                edges.append((u, v))

    return highway_nodes, edges, best_cost, all_nodes
