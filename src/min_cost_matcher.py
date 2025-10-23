import math
import operator
import logging

logger = logging.getLogger(__name__)

from src.utils.min_cost_flow import MinCostFlow


class MinCostMatcher:
    INF = int(1e9)

    def __init__(self, image_rgbs, frame_rgbs):
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

    def best_match(self):
        # Factor for the cost in order to determine the best matching
        factor = 1.1
        s, e = 0, 22
        best_cost = 1e20
        while e - s > 1:
            m = (e + s) >> 1
            logger.info(f"trying {m}...")
            try:
                _, cost = self.solve(m)
                logging.info(f"current cost: {cost}")
                if best_cost > cost:
                    best_cost = cost
                if cost > factor * best_cost:
                    # The cost is too much
                    raise Exception
                e = m
            except Exception:
                s = m
        logger.info(f"best capacity: {e}")
        return self.solve(e)[0]

    def solve(self, max_same_picture: int):
        assert max_same_picture > 0
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
            min_cost.add_edge(n + j, sink, max_same_picture, 0)
        min_cost.add_supply(source, n)
        min_cost.add_supply(sink, -n)
        min_cost.solve()
        order = []
        for i in range(n):
            t = min_cost.get_matched(i)
            if len(t) > 0 and len(t[0]) > 0:
                order.append(min_cost.get_matched(i)[0][0] - n)
            else:
                raise Exception("Invalid matching")
        return order, min_cost.total_cost
