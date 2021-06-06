import heapq


class Graph:
    def __init__(self, data):
        self.points = Graph.parse_data(data)

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

    def dijkstra(self, start_idx=None, end_idx=None):
        if start_idx is not None and start_idx not in self.points:
            raise ValueError('start_idx {} is not found'.format(start_idx))
        if end_idx is not None and end_idx not in self.points:
            raise ValueError('end_idx {} is not found'.format(end_idx))

        if start_idx is None:
            start_idx = min(self.points)

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
        if end_idx is None:
            return [[point_idx, weight, Graph.get_path(parents, point_idx)]
                    for point_idx, weight in weights.items()]
        return [end_idx, weights[end_idx], Graph.get_path(parents, end_idx)]

    @staticmethod
    def get_path(parents, end_idx):
        path = [end_idx]
        current = end_idx
        while parents[current] is not None:
            path.insert(0, parents[current])
            current = parents[current]
        return path
