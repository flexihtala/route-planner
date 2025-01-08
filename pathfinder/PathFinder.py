from pathfinder.utils.Point import Point
from pathfinder.utils.GeodesicCoordinates import GeodesicCoordinates
from pathfinder.utils.PlaneCoordinates import PlaneCoordinates
from pathfinder.utils.BDRequester import BDRequester


class PathFinder:
    meters_per_hour = 3000
    max_points = 10
    adequacy_ratio = 0.75

    def __init__(self, address: str | None, desired_time: float,
                 tags, points: set[Point] = None,
                 start_loc: GeodesicCoordinates = None) -> None:
        if start_loc is None:
            start_loc = BDRequester.get_geographic_coordinates(address)
        self.start_point = Point(start_loc)
        self.current_point = self.start_point
        self.desired_length = desired_time * PathFinder.meters_per_hour
        if points is None:
            self.points = BDRequester.get_points(start_loc,
                                                 self.desired_length,
                                                 tags)
        else:
            self.points = points
        self.points.add(self.start_point)
        self.plane_points = dict[Point, PlaneCoordinates]()
        for point in self.points:
            self.plane_points[point] = point.coordinates.convert_to_plane(
                self.current_point.coordinates)

    @staticmethod
    def get_path_length(path: list[Point]) -> float:
        length = 0
        for i in range(len(path) - 1):
            length += path[i].coordinates.get_distance_to(
                path[i + 1].coordinates)
        return length

    def find_path(self) -> list[Point]:
        return self.the_dumbest_greedy_algorithm()

    def the_dumbest_greedy_algorithm(self) -> list[Point]:
        path = self.greedy_with_indexes(self.points, self.start_point,
                                        self.desired_length, 0)
        path_length = self.get_path_length(path)
        if path_length < self.desired_length * self.adequacy_ratio and len(
                self.points) > self.max_points:
            path = self.greedy_with_indexes(self.points, self.start_point,
                                            self.desired_length, 1)
        return path

    def greedy_with_indexes(self, unused: set[Point], start_point: Point,
                            desired_length: float,
                            index_of_greed: int) -> list[Point]:
        path = []
        unused = set(unused)
        current_point = start_point
        remaining_length = desired_length
        plane_start_point = self.plane_points[start_point]
        path.append(current_point)
        unused.remove(current_point)
        while True:
            plane_current_point = self.plane_points[current_point]
            if not unused:
                break
            next_point = sorted(unused, key=lambda p: self.plane_points[
                p].get_distance_to(plane_current_point))[index_of_greed]
            plane_next_point = self.plane_points[next_point]
            remaining_length -= plane_current_point.get_distance_to(
                plane_next_point)
            if (plane_next_point.get_distance_to(
                    plane_start_point) > remaining_length
                    or len(path) >= self.max_points):
                break
            path.append(next_point)
            current_point = next_point
            unused.remove(next_point)
        path.append(self.start_point)
        return path
