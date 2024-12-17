from pathfinder.utils.GeodesicCoordinates import GeodesicCoordinates


class Point:
    def __init__(self, address: GeodesicCoordinates,
                 tags: set[str] = None):
        self.coordinates = address
        self.tags = tags

    def get_tags(self) -> set[str]:
        return self.tags

    def __repr__(self):
        return f'{self.coordinates}'

    @staticmethod
    def address_to_point(address):
        return Point(GeodesicCoordinates(latitude=address.lat,
                                         longitude=address.lon),
                     set(address.tags.values()))

    @staticmethod
    def art_object_to_point(art_object):
        return Point(GeodesicCoordinates(latitude=art_object.lat,
                                         longitude=art_object.lon),
                     {art_object.category})
