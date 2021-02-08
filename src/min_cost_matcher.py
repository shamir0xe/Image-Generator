import operator
import math
from ..libs.PythonLibrary.algorithms import MinCostFlow
from ..libs.PythonLibrary.utils import debug_text

class MinCostMatcher:
    INF = int(1e9)

    def __init__(self, image_rgbs, frame_rgbs, properties={}):
        self.max_same_picture = self.INF
        if 'max_same_picture' in properties:
            self.max_same_picture = properties['max_same_picture']
        image_array = []
        for i in range(len(image_rgbs)):
            image_array.extend(image_rgbs[i])
        self.image_rgbs = image_array
        self.frame_rgbs = frame_rgbs
    
    def __calc_distance(self, i, j):
        distance = tuple(map(operator.sub, self.image_rgbs[i], self.frame_rgbs[j]))
        distance = tuple(map(operator.pow, distance, (2, 2, 2)))
        distance = int(math.sqrt(sum(distance)))
        return distance

    def solve(self):
        n = len(self.image_rgbs)
        m = len(self.frame_rgbs)
        min_cost = MinCostFlow(n + m + 2)
        source = n + m
        sink = n + m + 1
        for i in range(n):
            min_cost.add_edge(source, i, 1, 0)
            for j in range(m):
                min_cost.add_edge(i, n + j, 1, self.__calc_distance(i, j))
        for j in range(m):
            min_cost.add_edge(n + j, sink, self.max_same_picture, 0)
        min_cost.add_supply(source, n)
        min_cost.add_supply(sink, -n)
        min_cost.solve()
        order = []
        for i in range(n):
            order.append(min_cost.get_matched(i)[0][0] - n)
        return order
