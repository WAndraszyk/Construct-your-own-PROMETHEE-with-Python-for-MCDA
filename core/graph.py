from collections import defaultdict
from typing import Any, DefaultDict, List


class Graph:
    """
    The Graph class represents a directed graph data structure
    """

    def __init__(self, vertices: int):
        """
        Constructs a new Graph instance with the given number of vertices.

        :param vertices: number of vertices in the graph
        """
        self.graph: DefaultDict[Any, list] = defaultdict(list)
        self.V = vertices

    def add_edge(self, u: int, v: int):
        """
        Adds a directed edge from vertex u to vertex v in the graph.

        :param u: first vertex
        :param v: second vertex
        """
        self.graph[u].append(v)

    def __is_cyclic_util__(
        self, v: int, visited: List[bool], recStack: List[bool]
    ) -> bool:
        """
        Checks for a given vertex if a cycle occurs.

        :param v: vertex
        :param visited: list of information about visiting vertexes
        :param recStack: recursion stack

        :return: True/False whether a cycle occurs
        """
        visited[v] = True
        recStack[v] = True

        for i in self.graph[v]:
            if not visited[i]:
                if self.__is_cyclic_util__(i, visited, recStack):
                    return True
            elif recStack[i]:
                return True

        recStack[v] = False
        return False

    def is_cyclic(self) -> bool:
        """
        Checks whether the graph contains a cycle.

        :return: True if the graph contains a cycle, and False otherwise.
        """
        visited = [False] * (self.V + 1)
        recStack = [False] * (self.V + 1)
        for node in range(self.V):
            if not visited[node]:
                if self.__is_cyclic_util__(node, visited, recStack):
                    return True
        return False

    def find_longest_path(self) -> int:
        """
        Calculates the length of the longest path in the graph.

        :return: the length of the longest path in the graph
        """
        n = self.V
        dp = [0] * n

        vis = [False] * n

        for i in range(n):
            if not vis[i]:
                self.__dfs__(i, self.graph, dp, vis)

        ans = 0

        for i in range(n):
            ans = max(ans, dp[i])

        return ans

    def __dfs__(
        self,
        node: int,
        adj: DefaultDict[Any, list],
        dp: List[int],
        vis: List[bool],
    ):
        """
        Depth-first search (DFS) algorithm.

        :param node: node index
        :param adj: graph default dict
        :param dp: list of paths lengths
        :param vis: list of information about visiting nodes
        """
        vis[node] = True

        for i in range(0, len(adj[node])):

            if not vis[adj[node][i]]:
                self.__dfs__(adj[node][i], adj, dp, vis)

            dp[node] = max(dp[node], 1 + dp[adj[node][i]])
