import random
import unittest
from web.pathfinder import BDRequests
from web.pathfinder import PathFinder
from pathfinder.utils.GeodesicCoordinates import GeodesicCoordinates
from pathfinder.utils.Point import Point


# привет эдик


class ApproximationTests(unittest.TestCase):
    def test_approximation_overlaps_area(self):
        self.approximation_test(GeodesicCoordinates(60, 60), 1000)

    def test_approximation_overlaps_area_on_big_length(self):
        self.approximation_test(GeodesicCoordinates(60, 60), 4000)

    def approximation_test(self, start_point: GeodesicCoordinates,
                           length: float):
        bdr = BDRequests()
        bottom_left, top_right = bdr.get_rectangle_approximation_of_area(
            start_point, length)
        distance_to_bottom = (GeodesicCoordinates(
            (top_right.latitude + bottom_left.latitude) / 2,
            bottom_left.longitude)
                              .convert_to_plane(start_point).get_length())
        distance_to_left = (GeodesicCoordinates(
            bottom_left.latitude,
            (bottom_left.longitude + top_right.longitude) / 2)
                            .convert_to_plane(start_point).get_length())
        distance_to_top = (GeodesicCoordinates(
            (top_right.latitude + bottom_left.latitude) / 2,
            bottom_left.longitude)
                           .convert_to_plane(start_point).get_length())
        distance_to_right = (GeodesicCoordinates(top_right.latitude, (
                bottom_left.longitude + top_right.longitude) / 2)
                             .convert_to_plane(start_point).get_length())

        self.assertGreater(distance_to_bottom, length)
        self.assertGreater(distance_to_left, length)
        self.assertGreater(distance_to_top, length)
        self.assertGreater(distance_to_right, length)


class PathFinderTests(unittest.TestCase):
    adequacy_ratio = 0.75

    def test_path_finder_returns_something(self):
        points = PathFinderTests.generate_points()
        pathfinder = PathFinder(None, 1, None, points,
                                GeodesicCoordinates(60, 60))
        self.assertGreater(len(pathfinder.find_path()), 2)

    def test_path_finder_returns_something_on_random(self):
        points = PathFinderTests.generate_random_points(
            GeodesicCoordinates(50, 50))
        pathfinder = PathFinder(None, 1, None, points,
                                GeodesicCoordinates(50, 50))
        self.assertGreater(len(pathfinder.find_path()), 2)

    def test_path_is_cyclic(self):
        points = PathFinderTests.generate_points()
        pathfinder = PathFinder(None, 1, None, points,
                                GeodesicCoordinates(60, 60))
        path = pathfinder.find_path()
        self.assertEquals(path[0], path[-1])

    def test_path_is_cyclic_on_random(self):
        points = PathFinderTests.generate_random_points(
            GeodesicCoordinates(60, 60))
        pathfinder = PathFinder(None, 1, None, points,
                                GeodesicCoordinates(60, 60))
        path = pathfinder.find_path()
        self.assertEquals(path[0], path[-1])

    def test_path_length_is_adequate(self):
        desired_time = 0.5
        points = PathFinderTests.generate_points()
        pathfinder = PathFinder(None, desired_time, None, points,
                                GeodesicCoordinates(60, 60))
        path = pathfinder.find_path()
        length = 0
        for i in range(len(path) - 1):
            length += path[i].coordinates.get_distance_to(
                path[i + 1].coordinates)
        least_length = (desired_time * pathfinder.meters_per_hour
                        * self.adequacy_ratio)
        self.assertGreater(length, least_length)

    def test_path_length_is_adequate_on_random(self):
        desired_time = 0.5
        points = PathFinderTests.generate_random_points(
            GeodesicCoordinates(60, 60))
        pathfinder = PathFinder(None, desired_time, None, points,
                                GeodesicCoordinates(60, 60))
        path = pathfinder.find_path()
        length = 0
        for i in range(len(path) - 1):
            length += path[i].coordinates.get_distance_to(
                path[i + 1].coordinates)
        least_length = (desired_time * pathfinder.meters_per_hour
                        * self.adequacy_ratio)
        self.assertGreater(length, least_length)

    @staticmethod
    def generate_points() -> set[Point]:
        return {Point(GeodesicCoordinates(60.0001, 60)),
                Point(GeodesicCoordinates(60, 60.0001)),
                Point(GeodesicCoordinates(60.0002, 60.0001)),
                Point(GeodesicCoordinates(59.9999, 59.9998)),
                Point(GeodesicCoordinates(59.998, 60.001)),
                Point(GeodesicCoordinates(60.002, 59.997)),
                Point(GeodesicCoordinates(59.997, 60.0001))}

    @staticmethod
    def generate_random_points(start_point: GeodesicCoordinates) -> set[Point]:
        result = set()
        length = random.randint(15, 20)
        for i in range(length):
            lat_delta = random.randint(-200, 200) / 100000
            long_delta = random.randint(-200, 200) / 100000
            point = Point(GeodesicCoordinates(start_point.latitude + lat_delta,
                                              start_point.longitude + long_delta))
            result.add(point)
        return result
