# Maximum Flow — Ford-Fulkerson / Edmonds-Karp

[![CI](https://github.com/BernardoFerrazG/max_flow/actions/workflows/ci.yml/badge.svg)](https://github.com/BernardoFerrazG/max_flow/actions/workflows/ci.yml)

A from-scratch implementation of the **Ford-Fulkerson method** for the maximum-flow problem, using **breadth-first search** to pick augmenting paths (the Edmonds-Karp variant). It reports the maximum flow value and the flow carried by each edge, and draws the network labelled `flow / capacity`.

NetworkX is used only to load and draw the network. The algorithm works on its own residual graph and is validated against `networkx.maximum_flow_value` in the test suite.

## How it works

1. Build the **residual graph**: each edge `u → v` with capacity `c` gets residual capacity `c`, plus a reverse edge `v → u` with residual capacity `0`.
2. Use **BFS** to find the shortest `s → t` path whose edges all have positive residual capacity.
3. Push the path's **bottleneck** (its smallest residual capacity) along it. Forward residuals decrease and reverse residuals increase, which lets later paths cancel earlier flow.
4. Repeat until no augmenting path exists. By the max-flow/min-cut theorem, the flow is then maximum.

| | |
| --- | --- |
| Time | `O(V · E²)` (Edmonds-Karp bound, independent of capacities) |
| Space | `O(V + E)` |

## Usage

```bash
pip install -r requirements.txt
python flow.py                       # network in graph.txt, source "s", sink "t"
python flow.py --no-plot
python flow.py -g net.txt -s A -t F
```

The input is a whitespace-separated edge list, one `u v capacity` per line (see [`graph.txt`](graph.txt)).

Example output:

```
Maximum flow from s to t: 70
Flow per edge (flow / capacity):
  s -> a: 30 / 50
  s -> c: 40 / 40
  a -> b: 30 / 60
  c -> b: 0 / 70
  c -> d: 40 / 60
  b -> t: 30 / 30
  d -> t: 40 / 50
```

## Tests

```bash
pip install pytest
pytest
```

The suite checks the flow value against NetworkX on the sample network and on 25 random networks. For every case it also checks that the reported per-edge flows are **valid**: each flow is within its edge's capacity, flow is conserved at every internal node, and the net outflow of the source equals the reported value. A dedicated test covers flow cancellation through reverse edges. CI runs the suite on every push.

## Project structure

```
flow.py              # residual graph, BFS augmenting paths, CLI and plotting
graph.txt            # sample network
tests/               # pytest suite
```
