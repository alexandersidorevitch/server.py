import heapq
from pprint import pprint


class Graph:
    def __init__(self, data):
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
                point_to_weight, point_to_idx = connection
                if point_to_idx not in checked_points and weight + point_to_weight < weights[point_to_idx]:
                    weights[point_to_idx] = weight + point_to_weight
                    parents[point_to_idx] = point_idx
                    heapq.heappush(heap, (weights[point_to_idx], point_to_idx))

            checked_points.add(point_idx)

        return {'line_idx': end_idx, 'weight': weights[end_idx], 'path': Graph.get_path(parents, end_idx)}

    @staticmethod
    def parse_data(data):
        points = dict(map(lambda point: (point.get('idx'), list()), data.get('points', tuple())))
        connections = map(lambda line: (line.get('points'), line.get('length')), data.get('lines', tuple()))

        for connection in connections:
            points_two, lenght = connection
            point_from, point_to = points_two
            points[point_from].append((lenght, point_to))
            points[point_to].append((lenght, point_from))
        return points

    @staticmethod
    def get_path(parents, end_idx):
        path = [{'line_idx': end_idx, 'speed': 0}]
        current = end_idx
        while parents[current] is not None:
            parent = parents[current]
            path.insert(0, {'line_idx': parent, 'speed': current - parent})
            current = parents[current]
        return path