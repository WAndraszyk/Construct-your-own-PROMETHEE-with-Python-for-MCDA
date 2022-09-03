from collections import defaultdict


class Graph:
    def __init__(self, vertices):
        self.graph = defaultdict(list)
        self.V = vertices

    def addEdge(self, u, v):
        self.graph[u].append(v)

    def __isCyclicUtil__(self, v, visited, recStack):

        visited[v] = True
        recStack[v] = True

        for i in self.graph[v]:
            if not visited[i]:
                if self.__isCyclicUtil__(i, visited, recStack):
                    return True
            elif recStack[i]:
                return True

        recStack[v] = False
        return False

    def isCyclic(self):
        visited = [False] * (self.V + 1)
        recStack = [False] * (self.V + 1)
        for node in range(self.V):
            if not visited[node]:
                if self.__isCyclicUtil__(node, visited, recStack):
                    return True
        return False

    def findLongestPath(self):
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

        vis[node] = True

        for i in range(0, len(adj[node])):

            if not vis[adj[node][i]]:
                self.__dfs__(adj[node][i], adj, dp, vis)

            dp[node] = max(dp[node], 1 + dp[adj[node][i]])
