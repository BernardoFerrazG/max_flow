"""Maximum flow with the Ford-Fulkerson method (Edmonds-Karp variant).

The network is read from a weighted edge list (``u v capacity`` per line).
Augmenting paths are found with breadth-first search over a residual graph
kept as plain dictionaries; NetworkX is used only to load and draw the network.
"""

from __future__ import annotations

import argparse
from collections import defaultdict, deque
from collections.abc import Hashable

import networkx as nx

Node = Hashable
Edge = tuple[Node, Node]


def load_network(path: str) -> nx.DiGraph:
    """Read a directed network whose edge weights are capacities."""
    return nx.read_weighted_edgelist(path, create_using=nx.DiGraph)


def _find_augmenting_path(
    residual: dict[Node, dict[Node, float]], source: Node, sink: Node
) -> list[Node] | None:
    """Shortest (fewest edges) source -> sink path with positive residual capacity."""
    parents: dict[Node, Node | None] = {source: None}
    queue = deque([source])
    while queue:
        node = queue.popleft()
        for neighbor, capacity in residual[node].items():
            if capacity > 0 and neighbor not in parents:
                parents[neighbor] = node
                if neighbor == sink:
                    path = [sink]
                    while parents[path[-1]] is not None:
                        path.append(parents[path[-1]])
                    return path[::-1]
                queue.append(neighbor)
    return None


def max_flow(network: nx.DiGraph, source: Node, sink: Node) -> tuple[float, dict[Edge, float]]:
    """Return ``(flow_value, flow_per_edge)`` for the original edges of ``network``.

    Edmonds-Karp: always augment along a shortest path, which bounds the
    number of augmentations by O(V E) and the running time by O(V E^2).
    """
    for node in (source, sink):
        if node not in network:
            raise KeyError(f"node {node!r} is not in the network")
    if source == sink:
        raise ValueError("source and sink must be different nodes")

    residual: dict[Node, dict[Node, float]] = defaultdict(dict)
    for u, v, capacity in network.edges(data="weight", default=0.0):
        if capacity < 0:
            raise ValueError(f"edge ({u}, {v}) has negative capacity")
        residual[u][v] = residual[u].get(v, 0.0) + capacity
        residual[v].setdefault(u, 0.0)

    value = 0.0
    while (path := _find_augmenting_path(residual, source, sink)) is not None:
        bottleneck = min(residual[u][v] for u, v in zip(path, path[1:]))
        for u, v in zip(path, path[1:]):
            residual[u][v] -= bottleneck
            residual[v][u] += bottleneck
        value += bottleneck

    # capacity(u, v) - residual(u, v) is the net flow from u to v. It is also
    # correct when the antiparallel edge (v, u) exists: then the residual entry
    # is shared, and only the direction with positive net flow carries any.
    flows: dict[Edge, float] = {
        (u, v): max(0.0, capacity - residual[u][v])
        for u, v, capacity in network.edges(data="weight", default=0.0)
    }
    return value, flows


def draw_network(network: nx.DiGraph, flows: dict[Edge, float]) -> None:
    import matplotlib.pyplot as plt

    pos = nx.spring_layout(network, seed=42)
    nx.draw(network, pos, with_labels=True, node_color="lightblue", node_size=600, arrowsize=20)
    labels = {(u, v): f"{flows[(u, v)]:g}/{c:g}" for u, v, c in network.edges(data="weight")}
    nx.draw_networkx_edge_labels(network, pos, edge_labels=labels)
    plt.title("flow / capacity")
    plt.show()


def main() -> None:
    parser = argparse.ArgumentParser(description="Maximum flow (Edmonds-Karp).")
    parser.add_argument("-g", "--graph", default="graph.txt", help="edge-list file (default: graph.txt)")
    parser.add_argument("-s", "--source", default="s", help="source node (default: s)")
    parser.add_argument("-t", "--sink", default="t", help="sink node (default: t)")
    parser.add_argument("--no-plot", action="store_true", help="do not open the network window")
    args = parser.parse_args()

    network = load_network(args.graph)
    value, flows = max_flow(network, args.source, args.sink)

    print(f"Maximum flow from {args.source} to {args.sink}: {value:g}")
    print("Flow per edge (flow / capacity):")
    for (u, v), flow in flows.items():
        print(f"  {u} -> {v}: {flow:g} / {network[u][v]['weight']:g}")

    if not args.no_plot:
        draw_network(network, flows)


if __name__ == "__main__":
    main()
