import pymap3d as pm
from pathfinder.utils.PlaneCoordinates import PlaneCoordinates


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

    def get_distance_to(self, other):
        other_plane = other.convert_to_plane(self)
        self_plane = self.convert_to_plane(self)
        return self_plane.get_distance_to(other_plane)

    def __repr__(self):
        return f'{self.latitude},{self.longitude}'
