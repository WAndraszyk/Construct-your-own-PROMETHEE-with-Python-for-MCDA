from collections import defaultdict


class Graph:
    """
        The Graph class represents a directed graph data structure
    """
    def __init__(self, vertices):
        """
            Constructs a new Graph instance with the given number of vertices.
        """
        self.graph = defaultdict(list)
        self.V = vertices

    def add_edge(self, u, v):
        """
            Adds a directed edge from vertex u to vertex v in the graph.
        """
        self.graph[u].append(v)

    def __is_cyclic_util__(self, v, visited, recStack):
        """
            Checks for a given vertex if a cycle occurs.
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

    def is_cyclic(self):
        """
            Returns True if the graph contains a cycle, and False otherwise.
        """
        visited = [False] * (self.V + 1)
        recStack = [False] * (self.V + 1)
        for node in range(self.V):
            if not visited[node]:
                if self.__is_cyclic_util__(node, visited, recStack):
                    return True
        return False

    def find_longest_path(self):
        """
            Returns the length of the longest path in the graph.
        """
        n = self.V
        dp = [0] * (n + 1)

        vis = [False] * (n + 1)

        for i in range(1, n + 1):
            if not vis[i]:
                self.__dfs__(i, self.graph, dp, vis)

        ans = 0

        for i in range(1, n + 1):
            ans = max(ans, dp[i])

        return ans

    def __dfs__(self, node, adj, dp, vis):
        """
            Depth-first search (DFS) algorithm.
        """
        vis[node] = True

        for i in range(0, len(adj[node])):

            if not vis[adj[node][i]]:
                self.__dfs__(adj[node][i], adj, dp, vis)

            dp[node] = max(dp[node], 1 + dp[adj[node][i]])
