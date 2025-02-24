import networkx as nx
import matplotlib.pyplot as plt


def create_graph(file_path):
    G = nx.read_weighted_edgelist(file_path, create_using= nx.DiGraph)
    return G

def draw_graph(graph):

    pos = nx.spring_layout(graph) 
    nx.draw(graph, pos, with_labels=True, arrowsize=20)
    labels = nx.get_edge_attributes(graph, 'weight')  
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=labels)
    plt.show()


def ford_fulkerson(graph, source, sink):

    residual_graph = graph.copy()  
    for u, v in residual_graph.edges():
        if 'weight' not in residual_graph[u][v]:
            residual_graph[u][v]['weight'] = 0

    max_flow = 0
    elemental_flow = {}  

    while True:
        
        path, path_flow = find_path(residual_graph, source, sink)

        if path_flow == 0:
            break 

        # Update the residual flow along the path
        for u, v in zip(path[:-1], path[1:]):
            residual_graph[u][v]['weight'] -= path_flow
            if residual_graph.has_edge(v, u):
                residual_graph[v][u]['weight'] += path_flow
            else:
                residual_graph.add_edge(v, u, weight=path_flow)

            if (u, v) in elemental_flow:
                elemental_flow[(u, v)] += path_flow
            else:
                elemental_flow[(u, v)] = path_flow

        max_flow += path_flow

    return max_flow, elemental_flow


def find_path(graph, source, sink, visited=None):
 
    if visited is None:
        visited = set()

    if source == sink:
        return [sink], float('Inf')

    visited.add(source)

    for neighbor in graph.neighbors(source):
        capacity = graph[source][neighbor]['weight']
        if neighbor not in visited and capacity > 0:
            path, path_flow = find_path(graph, neighbor, sink, visited)
            if path:
                return [source] + path, min(path_flow, capacity)

    return [], 0


def main():
    file_path = 'graph.txt'
    G = create_graph(file_path)

    draw_graph(G)

    source = 's'  
    sink = 't'  

    # Calculate the maximum flow and the elemental flow in each edge
    max_flow, elemental_flow = ford_fulkerson(G, source, sink)

    print(f"Maximum flow: {max_flow}")
    
    # Display the elemental flow in each edge
    print("Elemental flow in each edge:")
    for edge, flow in elemental_flow.items():
        print(f"Edge {edge}: Flow {flow}")

main()
