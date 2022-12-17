"""
This module implements the Ordered Clustering method which divides
alternatives into k ordered clusters based on the preference
indices matrix
"""
from typing import List, Tuple
from core.aliases import NumericValue
from core.input_validation import ordered_clustering_validation
from core.graph import Graph
import numpy as np
import pandas as pd

__all__ = ["group_into_ordered_clusters"]


def group_into_ordered_clusters(preferences: pd.DataFrame, k: int
                                ) -> pd.Series:
    """
    Divides alternatives into k ordered clusters based on the preference
    indices matrix.

    :param preferences: DataFrame of preference indices as value,
        alternatives/profiles as index and columns
    :param k: number of clusters
    :return: Series of alternatives grouped into k ordered clusters,
     index: cluster number
    """
    # input data validation
    ordered_clustering_validation(preferences, k)

    alternatives = preferences.index
    shape = np.shape(preferences)
    preferences = list(preferences.values)

    graph = np.zeros(shape)
    clusters = []
    deleted_nodes = []
    while True:
        # find maximum preference value
        max_pi, i, j = _search_max(preferences)
        if max_pi == 0:
            break
        else:
            # add edge between node i and j
            graph[i][j] = 1
            #  check if the graph has no cycle or path longer than k − 1
            if _check_graph(graph, k):
                # delete the edge between node i and j
                graph[i][j] = 0
            preferences[i][j] = 0

    while True:
        cluster = []
        # calculate input degree of all nodes in the graph
        degrees, no_edges = _calculate_degrees(graph)
        if no_edges:
            for i in range(len(degrees)):
                # create last cluster with remaining nodes
                if i not in deleted_nodes:
                    cluster.append(alternatives[i])
            clusters.append(cluster)
            break
        # create a cluster by finding all nodes with input degree equal to 0
        for i in range(len(degrees)):
            if degrees[i] == 0 and i not in deleted_nodes:
                cluster.append(alternatives[i])
                _delete_node(graph, i)
                deleted_nodes.append(i)
        clusters.append(cluster)
    clusters_fin = pd.Series(clusters, name='Alternatives in clusters')
    clusters_fin.index += 1
    return clusters_fin


def _search_max(preferences: List[List[NumericValue]]
                ) -> Tuple[NumericValue, int, int]:
    """
    This function searches for the maximum value in preference matrix.

    :param preferences: matrix of preference indices
    :return: Tuple of maximum preference value and its position in matrix
    """
    max_pi = 0
    pi_i = 0
    pi_j = 0
    # iterate through preference indices and find the maximum
    for i in range(len(preferences)):
        for j in range(len(preferences[0])):
            if preferences[i][j] > max_pi:
                # set the new maximum value
                max_pi = preferences[i][j]
                # set the value's row
                pi_i = i
                # set the value's column
                pi_j = j

    return max_pi, pi_i, pi_j


def _check_graph(graph: np.ndarray, k: int) -> bool:
    """
    This function checks if the graph has no cycle or path longer than k − 1.

    :param graph: graph which takes alternatives for nodes
     in a form of a ndarray
    :param k: number of clusters

    :return: True if the graph has a cycle or path longer than k − 1,
        False otherwise
    """
    # create Graph object
    g = Graph(len(graph))
    # add edges to Graph according to graph matrix
    for i in range(len(graph)):
        for j in range(len(graph[0])):
            if graph[i][j] == 1:
                g.add_edge(i, j)

    # check for cycles in Graph
    is_cyclic = g.is_cyclic()
    if not is_cyclic:
        # check the maximum path length
        return g.find_longest_path() >= k - 1
    else:
        return True


def _calculate_degrees(graph: np.ndarray) -> Tuple[List[int], bool]:
    """
    This function calculates input degrees of nodes in the graph and
    checks if there are nodes left in it.

    :param graph: graph which takes alternatives for nodes
     in a form of a ndarray

    :return: Tuple of list of nodes' input degrees and boolean value of
        True/False whether there are edges left in the graph
    """
    degrees = []
    no_edges = True
    for j in range(len(graph)):
        degree = 0
        # search for edges in graph
        for i in range(len(graph[0])):
            if graph[i][j] == 1:
                degree += 1
                no_edges = False
        degrees.append(degree)
    return degrees, no_edges


def _delete_node(graph: np.ndarray, row: int):
    """
    This function deletes a node in the graph.

    :param graph: graph which takes alternatives for nodes
     in a form of a ndarray
    :param row: row in the graph ndarray
    """
    for i in range(len(graph[row])):
        graph[row][i] = 0
        graph[i][row] = 0
