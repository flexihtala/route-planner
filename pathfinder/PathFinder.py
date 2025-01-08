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
        index_of_greed = 0
        path = self.greedy_with_shifts(self.points, self.start_point,
                                       self.desired_length, index_of_greed)
        default_length = len(path)
        path_length = self.get_path_length(path)
        while path_length < self.desired_length * self.adequacy_ratio and len(
                self.points) - default_length > index_of_greed:
            path_length = self.get_path_length(path)
            index_of_greed += 1
            try:
                a = self.greedy_with_shifts(self.points, self.start_point,
                                            self.desired_length,
                                            index_of_greed, 3)
                path = a
            except Exception:
                break
        return path

    def greedy_with_shifts(self, unused: set[Point], start_point: Point,
                           desired_length: float,
                           shift_amplitude: int = 0,
                           shift_frequency: int = 0) -> list[Point]:
        path = []
        local_unused = set(unused)
        current_point = start_point
        remaining_length = desired_length
        plane_start_point = self.plane_points[start_point]
        path.append(current_point)
        local_unused.remove(current_point)
        shift_counter = 0
        while True:
            shift_counter += 1
            shift = 0
            if shift_frequency == shift_counter:
                shift += shift_amplitude
                shift_counter = 0
            plane_current_point = self.plane_points[current_point]
            if not local_unused:
                break
            next_point = sorted(local_unused, key=lambda p: self.plane_points[
                p].get_distance_to(plane_current_point))[shift]
            plane_next_point = self.plane_points[next_point]
            remaining_length -= plane_current_point.get_distance_to(
                plane_next_point)
            if (plane_next_point.get_distance_to(
                    plane_start_point) > remaining_length
                    or len(path) >= self.max_points):
                break
            path.append(next_point)
            current_point = next_point
            local_unused.remove(next_point)
        path.append(self.start_point)
        return path
