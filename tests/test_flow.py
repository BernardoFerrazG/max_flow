import random
from pathlib import Path

import networkx as nx
import pytest

from flow import load_network, max_flow

GRAPH_FILE = Path(__file__).resolve().parent.parent / "graph.txt"


def assert_valid_flow(network, flows, source, sink, value):
    for (u, v), flow in flows.items():
        assert 0 <= flow <= network[u][v]["weight"] + 1e-9
    for node in network.nodes:
        if node in (source, sink):
            continue
        inflow = sum(flows[(u, node)] for u in network.predecessors(node))
        outflow = sum(flows[(node, v)] for v in network.successors(node))
        assert inflow == pytest.approx(outflow)
    out_of_source = sum(flows[(source, v)] for v in network.successors(source))
    into_source = sum(flows[(u, source)] for u in network.predecessors(source))
    assert out_of_source - into_source == pytest.approx(value)


def test_sample_network():
    network = load_network(GRAPH_FILE)
    value, flows = max_flow(network, "s", "t")
    assert value == nx.maximum_flow_value(network, "s", "t", capacity="weight")
    assert_valid_flow(network, flows, "s", "t", value)


@pytest.mark.parametrize("seed", range(25))
def test_random_networks_match_networkx(seed):
    rng = random.Random(seed)
    network = nx.gnp_random_graph(15, 0.3, seed=seed, directed=True)
    for u, v in network.edges:
        network[u][v]["weight"] = rng.randint(1, 20)

    value, flows = max_flow(network, 0, 14)
    assert value == nx.maximum_flow_value(network, 0, 14, capacity="weight")
    assert_valid_flow(network, flows, 0, 14, value)


def test_flow_cancellation_is_reported_correctly():
    # Classic case where the second augmenting path must push flow back over b -> a.
    network = nx.DiGraph()
    for u, v, c in [("s", "a", 1), ("s", "b", 1), ("b", "a", 1), ("a", "t", 1), ("b", "t", 1)]:
        network.add_edge(u, v, weight=c)
    value, flows = max_flow(network, "s", "t")
    assert value == 2
    assert_valid_flow(network, flows, "s", "t", value)


def test_invalid_nodes():
    network = load_network(GRAPH_FILE)
    with pytest.raises(KeyError):
        max_flow(network, "s", "z")
    with pytest.raises(ValueError):
        max_flow(network, "s", "s")
