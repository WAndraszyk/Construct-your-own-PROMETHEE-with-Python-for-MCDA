from typing import List, Tuple
from core.aliases import NumericValue
from core.input_validation import ordered_clustering_validation
from core.graph import Graph
import numpy as np
import pandas as pd

__all__ = ["group_into_ordered_clusters"]


def group_into_ordered_clusters(preferences: pd.DataFrame, k: int) -> pd.Series:
    """
    Divides alternatives into k ordered clusters based on the preference indices matrix.

    :param preferences: preference indices of alternatives over alternatives
    :param k: number of clusters
    :return: alternatives grouped into k ordered clusters
    """
    ordered_clustering_validation(preferences, k)

    alternatives = preferences.index
    shape = np.shape(preferences)
    preferences = preferences.values.tolist()

    graph = np.zeros(shape)
    clusters = []
    deleted_nodes = []
    while True:
        max_pi, i, j = _search_max(preferences)
        if max_pi == 0:
            break
        else:
            graph[i][j] = 1
            if _check_graph(graph, k):
                graph[i][j] = 0
            preferences[i][j] = 0
    while True:
        cluster = []
        degrees, no_nodes = _calculate_degrees(graph)
        if no_nodes:
            for i in range(len(degrees)):
                if i not in deleted_nodes:
                    cluster.append(alternatives[i])
            clusters.append(cluster)
            break
        for i in range(len(degrees)):
            if degrees[i] == 0 and i not in deleted_nodes:
                cluster.append(alternatives[i])
                _delete_node(graph, i)
                deleted_nodes.append(i)
        clusters.append(cluster)
    clusters_fin = pd.Series(clusters, name='Alternatives in clusters')
    clusters_fin.index += 1
    return clusters_fin


def _search_max(preferences: List[List[NumericValue]]) -> Tuple[NumericValue, int, int]:
    max_pi = 0
    pi_i = 0
    pi_j = 0
    for i in range(len(preferences)):
        for j in range(len(preferences[0])):
            if preferences[i][j] > max_pi:
                max_pi = preferences[i][j]
                pi_i = i
                pi_j = j
    return max_pi, pi_i, pi_j


def _check_graph(graph: np.ndarray, k: int) -> bool:
    g = Graph(len(graph))
    for i in range(len(graph)):
        for j in range(len(graph[0])):
            if graph[i][j] == 1:
                g.add_edge(i, j)
    is_cyclic = g.is_cyclic()
    if not is_cyclic:
        return g.find_longest_path() >= k - 1
    else:
        return True


def _calculate_degrees(graph: np.ndarray) -> Tuple[List[int], bool]:
    degrees = []
    no_nodes = True
    for j in range(len(graph)):
        degree = 0
        for i in range(len(graph[0])):
            if graph[i][j] == 1:
                degree += 1
                no_nodes = False
        degrees.append(degree)
    return degrees, no_nodes


def _delete_node(graph: np.ndarray, row: int) -> None:
    for i in range(len(graph[row])):
        graph[row][i] = 0
        graph[i][row] = 0
