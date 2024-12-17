from pathfinder.utils.Point import Point
from pathfinder.utils.GeodesicCoordinates import GeodesicCoordinates
from pathfinder.utils.PlaneCoordinates import PlaneCoordinates
from pathfinder.utils.BDRequester import BDRequester



class PathFinder:
    meters_per_hour = 3000

    def __init__(self, address: str, desired_time: float,
                 tags, points: set[Point] = None,
                 start_loc: GeodesicCoordinates = None) -> None:
        if start_loc is None:
            start_loc = BDRequester.get_geographic_coordinates(address)
        self.start_point = Point(start_loc)
        self.current_point = self.start_point
        self.desired_length = desired_time * PathFinder.meters_per_hour
        if points is None:
            self.points = BDRequester.get_points(start_loc, self.desired_length,
                                                tags)
        else:
            self.points = points
        self.points.add(self.start_point)
        self.plane_points = dict[Point, PlaneCoordinates]()
        for point in self.points:
            self.plane_points[point] = point.coordinates.convert_to_plane(
                self.current_point.coordinates)

    def find_path(self) -> list[Point]:
        return self.the_dumbest_greedy_algorithm()

    def the_dumbest_greedy_algorithm(self) -> list[Point]:
        path = []
        unused = set(self.points)
        current_point = self.start_point
        remaining_length = self.desired_length
        plane_start_point = self.plane_points[self.start_point]
        while True:
            plane_current_point = self.plane_points[current_point]
            if not unused:
                break
            closest_point = min(unused, key=lambda p: self.plane_points[
                p].get_distance_to(plane_current_point))
            plane_closest_point = self.plane_points[closest_point]
            remaining_length -= plane_current_point.get_distance_to(
                plane_closest_point)
            if plane_closest_point.get_distance_to(
                    plane_start_point) > remaining_length:
                break
            path.append(closest_point)
            current_point = closest_point
            unused.remove(closest_point)
        path.append(self.start_point)
        return path