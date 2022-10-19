from core.aliases import PreferencesTable
from core.Graph import Graph
import numpy as np
import pandas as pd


class OrderedClustering:
    def __init__(self, preferences: PreferencesTable):
        self.alternatives = preferences.index
        self.shape = np.shape(preferences)
        self.preferences = preferences.values.tolist()

    def group_alternatives(self, clusters_no: int):
        graph = np.zeros(self.shape)
        clusters = []
        deleted_nodes = []
        while True:
            max_pi, i, j = self.__search_max__()
            if max_pi == 0:
                break
            else:
                graph[i][j] = 1
                if self.__check_graph__(graph, clusters_no):
                    graph[i][j] = 0
                self.preferences[i][j] = 0
        while True:
            cluster = []
            degrees, no_nodes = self.__calculate_degrees__(graph)
            if no_nodes:
                break
            for i in range(len(degrees)):
                if degrees[i] == 0 and i not in deleted_nodes:
                    cluster.append(self.alternatives[i])
                    self.__delete_node__(graph, i)
                    deleted_nodes.append(i)
            clusters.append(cluster)
        return pd.Series(clusters, name='Alternatives in clusters')

    def __search_max__(self):
        max_pi = 0
        pi_i = 0
        pi_j = 0
        for i in range(len(self.preferences)):
            for j in range(len(self.preferences[0])):
                if self.preferences[i][j] > max_pi:
                    max_pi = self.preferences[i][j]
                    pi_i = i
                    pi_j = j
        return max_pi, pi_i, pi_j

    def __check_graph__(self, graph, K):
        g = Graph(len(graph))
        for i in range(len(graph)):
            for j in range(len(graph[0])):
                if graph[i][j] == 1:
                    g.addEdge(i, j)
        is_cyclic = g.isCyclic()
        if not is_cyclic:
            return g.findLongestPath() > K-1
        else:
            return True

    def __calculate_degrees__(self, graph):
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

    def __delete_node__(self, graph, row):
        for i in range(len(graph[row])):
            graph[row][i] = 0
            graph[i][row] = 0
