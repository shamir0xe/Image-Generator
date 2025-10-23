from ortools.graph.python import min_cost_flow


class MinCostFlow:
    def __init__(self, n):
        self.n = n
        self.__maxflow = min_cost_flow.SimpleMinCostFlow()

    def add_edge(self, u, v, capacity, weight):
        self.__maxflow.add_arc_with_capacity_and_unit_cost(u, v, capacity, weight)

    def add_supply(self, u, supply):
        self.__maxflow.set_node_supply(u, supply)

    def get_matched(self, u):
        return self.__edges[u]

    def solve(self):
        self.__edges = [[] for _ in range(self.n)]
        if self.__maxflow.solve() == self.__maxflow.OPTIMAL:
            self.total_cost = self.__maxflow.optimal_cost()
            # print('Minimum cost:', self.total_cost)
            for i in range(self.__maxflow.num_arcs()):
                u = self.__maxflow.tail(i)
                v = self.__maxflow.head(i)
                f = self.__maxflow.flow(i)
                if f > 0:
                    self.__edges[u].append((v, f))
            return True
        else:
            print("There was an issue with the min cost flow input.")
            return False
