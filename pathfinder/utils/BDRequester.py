import math
from pathfinder.utils.GeodesicCoordinates import GeodesicCoordinates
from db.APIYandex import YandexApiGeocoderParser
from db.DatabaseConnector import DatabaseConnector
from pathfinder.utils.Point import Point


class BDRequester:
    bd = None
    approximation_delta = 0.00001
    length_approximation_ratio = math.sqrt(2) * 1.2

    @staticmethod
    def get_geographic_coordinates(address: str) -> GeodesicCoordinates:
        parser = YandexApiGeocoderParser()
        response = parser.get_cords(address)
        return GeodesicCoordinates(response[1], response[0])

    @staticmethod
    def get_points(start_point: GeodesicCoordinates, length: float, tags) \
            -> set[Point]:
        length = math.sqrt(2) * length
        bottom_left, top_right = BDRequester.get_rectangle_approximation_of_area(
            start_point, length)
        db = DatabaseConnector()
        response = db.get_answer(bottom_left.longitude, top_right.longitude,
                                 bottom_left.latitude, top_right.latitude,
                                 tags)
        return set(response)

    @staticmethod
    def get_rectangle_approximation_of_area(start_point: GeodesicCoordinates,
                                            length: float) \
            -> tuple[GeodesicCoordinates, GeodesicCoordinates]:
        length = length * BDRequester.length_approximation_ratio
        bottom_left = GeodesicCoordinates(start_point.latitude,
                                          start_point.longitude)
        top_right = GeodesicCoordinates(start_point.latitude,
                                        start_point.longitude)
        while True:
            bottom_left.latitude -= BDRequester.approximation_delta
            bottom_left.longitude -= BDRequester.approximation_delta * 2
            if bottom_left.convert_to_plane(
                    start_point).get_length() >= length:
                break
        while True:
            top_right.latitude += BDRequester.approximation_delta
            top_right.longitude += BDRequester.approximation_delta * 2
            if top_right.convert_to_plane(start_point).get_length() >= length:
                break
        return bottom_left, top_right
