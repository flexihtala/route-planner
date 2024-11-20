import math
import pymap3d as pm
import Address
import APIYandex
from collections import deque

class PlaneCoordinates:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def get_distance_to(self, other) -> float:
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def get_length(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)


class GeodesicCoordinates:
    def __init__(self, latitude: float, longitude: float):
        self.latitude = latitude
        self.longitude = longitude

    def convert_to_plane(self, conversion_point) -> PlaneCoordinates:
        result = pm.geodetic2enu(self.latitude, self.longitude, 0,
                                 conversion_point.latitude,
                                 conversion_point.longitude,
                                 0)
        return PlaneCoordinates(result[0], result[1])

    def __repr__(self):
        return f'{self.latitude},{self.longitude}'


class Point:
    def __init__(self, address: GeodesicCoordinates,
                 tags: set[str] = None):
        self.coordinates = address
        self.tags = tags

    def get_tags(self) -> set[str]:
        return self.tags

    def __repr__(self):
        return f'{self.coordinates}'


class BDRequests:
    bd = None

    @staticmethod
    def get_geographic_coordinates(address: str) -> GeodesicCoordinates:
        parser = APIYandex.YandexApiGeocoderParser()
        response = parser.get_cords(address)
        return GeodesicCoordinates(response[1], response[0])

    @staticmethod
    def get_points(start_point: GeodesicCoordinates, length: float, tags) \
            -> set[Point]:
        length = math.sqrt(2) * length
        delta = 0.000001
        bottom_left = GeodesicCoordinates(start_point.latitude,
                                          start_point.longitude)
        top_right = GeodesicCoordinates(start_point.latitude,
                                        start_point.longitude)
        while True:
            bottom_left.latitude -= delta
            bottom_left.longitude -= delta
            if bottom_left.convert_to_plane(
                    start_point).get_length() >= length:
                break
        while True:
            top_right.latitude += delta
            top_right.longitude += delta
            if top_right.convert_to_plane(start_point).get_length() >= length:
                break
        db = Address.DatabaseConnector()
        db.connect_to_db()
        response = db.get_answer(bottom_left.longitude, top_right.longitude,
                                 bottom_left.latitude, top_right.latitude,
                                 tags)
        points = set()
        db.close_data_base()
        for point in response:
            address = GeodesicCoordinates(point.lat, point.lon)
            points.add(Point(address, point.amenity))
        return points


class PathFinder:
    meters_per_hour = 3000
    len_ratio = 1.3

    def __init__(self, address: str, desired_time: float,
                 tags) -> None:
        start_loc = BDRequests.get_geographic_coordinates(address)
        self.start_point = Point(start_loc)
        self.current_point = self.start_point
        self.desired_length = desired_time * PathFinder.meters_per_hour
        self.points = BDRequests.get_points(start_loc, self.desired_length,
                                            tags)
        self.points.add(self.start_point)
        self.plane_points = dict[Point, PlaneCoordinates]()
        self.update_distances()
        self.graph = self.build_graph()

    def find_path(self) -> list[Point]:
        paths = self.find_all_paths()
        sorted_paths = sorted(paths, key=lambda p: len(p), reverse=True)
        return sorted_paths[0]

    def build_graph(self) -> dict[Point, list[tuple[Point, float]]]:
        stack = deque()
        stack.append(self.start_point)
        points = self.points
        unused = set(self.points)
        result = {}
        while stack:
            point = stack.popleft()
            if point not in unused:
                continue
            unused.remove(point)
            plane_point = self.plane_points[point]
            points.remove(point)
            if not unused:
                break
            closest_point = min(unused,
                                key=lambda p: self.plane_points[
                                    p].get_distance_to(plane_point))
            points.add(point)
            len_range = self.plane_points[closest_point].get_distance_to(
                plane_point) * PathFinder.len_ratio
            neighbor_points = list(
                filter(lambda p: self.plane_points[p].get_distance_to(
                    plane_point) <= len_range, self.plane_points.keys()))
            # neighbor_points = list(
            #     map(lambda p: (
            #         p, self.plane_points[p].get_distance_to(plane_point)),
            #         neighbor_points))
            neighbors = []
            for neighbor_point in neighbor_points:
                if neighbor_point in unused:
                    stack.append(neighbor_point)
                if neighbor_point != point:
                    neighbors.append(neighbor_point)
            result[point] = neighbors
        return result

    def find_all_paths(self) -> list[list[Point]]:
        paths = list[list[Point]]()
        path = []
        unused = set(self.points)
        remaining_length = self.desired_length
        stack = [(self.current_point, 0, remaining_length)]
        previous_point = self.start_point
        while stack:
            popped = stack.pop()
            self.current_point = popped[0]
            depth = popped[1]
            remaining_length = popped[2]
            for point in path[depth: len(path)]:
                unused.add(point)
            path = path[0:depth]
            if path:
                previous_point = path[-1]
            path.append(self.current_point)
            unused.remove(self.current_point)
            # self.update_distances()
            remaining_length -= self.plane_points[
                previous_point].get_distance_to(
                self.plane_points[self.current_point])
            if (self.plane_points[self.current_point].
                    get_distance_to(self.plane_points[self.start_point])
                    > remaining_length):
                unused.add(path.pop())
                path.append(self.start_point)
                paths.append(list(path))
                print(len(paths))
                path.pop()
                continue
            if not unused:
                path.append(self.start_point)
                paths.append(list(path))
                print(len(paths))
                path.pop()
                continue
            for next_loc in self.graph[self.current_point]:
                stack.append((next_loc, len(path), remaining_length))
        self.current_point = self.start_point
        return paths

    def update_distances(self):
        for point in self.points:
            self.plane_points[point] = point.coordinates.convert_to_plane(
                self.current_point.coordinates)


if __name__ == '__main__':
    pf = PathFinder('Фонвизина 8', 0.25, ['bar'])
    #     points = {Point(GeodesicCoordinates(0.01, -0.01)),
    #               Point(GeodesicCoordinates(0.01, 0.01)),
    #               Point(GeodesicCoordinates(0.02, 0.02)),
    #               Point(GeodesicCoordinates(0.03, 0.00))}
    #     pathfinder = PathFinder(GeodesicCoordinates(0, 0), points, 7)
    paaths = pf.find_all_paths()
    paath = pf.find_path()
    print(paath)
