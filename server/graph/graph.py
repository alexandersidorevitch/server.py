import heapq
from pprint import pprint


class Graph:
    def __init__(self, data, ):
        self.points = Graph.parse_data(data)

    def dijkstra(self, start_idx, end_idx):
        if start_idx not in self.points:
            raise ValueError('start_idx {} is not found'.format(start_idx))
        if end_idx not in self.points:
            raise ValueError('end_idx {} is not found'.format(end_idx))

        heap = [(0, start_idx)]
        parents = {point_idx: None for point_idx in self.points}
        checked_points = set()
        weights = {point_idx: float('inf') for point_idx in self.points}
        weights[start_idx] = 0

        while heap:
            weight, point_idx = heapq.heappop(heap)
            if point_idx in checked_points:
                continue
            for connection in self.points[point_idx]:
                point_to_weight, point_to_idx, line_idx = connection
                if point_to_idx not in checked_points and weight + point_to_weight < weights[point_to_idx]:
                    weights[point_to_idx] = weight + point_to_weight
                    parents[point_to_idx] = point_idx
                    heapq.heappush(heap, (weights[point_to_idx], point_to_idx))

            checked_points.add(point_idx)

        return {'line_idx': end_idx, 'weight': weights[end_idx], 'path': self.get_path(parents, end_idx)}

    def get_path(self, parents, end_idx):
        path = []
        current = end_idx
        while parents[current] is not None:
            parent = parents[current]
            path.insert(0, {
                'line_idx': next(filter(lambda connection: connection[1] == parent,
                                        self.points[current]))[2],
                'speed': 1 if current > parent else -1}
                        )
            current = parents[current]
        return path

    @staticmethod
    def parse_data(data):
        points = dict(map(lambda point: (point.get('idx'), list()), data.get('points', tuple())))
        connections = map(lambda line: (line.get('points'), line.get('length'), line.get('idx')),
                          data.get('lines', tuple()))

        for connection in connections:
            two_points, length, line_idx = connection
            from_point, to_point = two_points
            points[from_point].append((length, to_point, line_idx))
            points[to_point].append((length, from_point, line_idx))
        return points
