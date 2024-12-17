from sqlalchemy import create_engine, and_
from sqlalchemy.orm import scoped_session, sessionmaker

from db.utils.Address import Address
from db.utils.ArtObject import ArtObject
from pathfinder.utils.Point import Point


class DatabaseConnector:

    _url = 'postgresql://upisxsl8ebyt76zvmwdc:k7W50CFPTAjR3GsTHZL2PrTQsSV4ud@b19mrygsbv2ejyfwxeb8-postgresql.services.clever-cloud.com:50013/b19mrygsbv2ejyfwxeb8'

    tags: list[str] = [
        'theatre',
        'restaurant',
        'bar',
        'arts_centre',
        'social_facility',
        'cafe',
        'hookah_lounge',
        'pub',
        'fast_food',
        'place_of_worship',
        'library',
        'university',
        'art_object'
    ]

    def __init__(self):
        self.engine = self._create_engine()
        self.Session = scoped_session(sessionmaker(bind=self.engine))
        self.session = self.Session()

    def _create_engine(self):
        return create_engine(self._url, echo=False)

    def get_answer(self, min_lon: float, max_lon: float,
                   min_lat: float, max_lat: float, tags=None) -> list[Point]:
        """
        Выдает список объектов, находящихся в заданных диапахонах с нужными
        тегами и всегда с арт объектами
        :param min_lon: минимальная долгота
        :param max_lon: максимальная долгота
        :param min_lat: минимальная широта
        :param max_lat: максимальная широта
        :param tags: (по умолчанию стоят все) типы объектов
        :return: список из точек, тип которых или Address, или ArtObject
        """
        if tags is None:
            tags = self.tags

        query_filters = [
            Address.lon.between(min_lon, max_lon),
            Address.lat.between(min_lat, max_lat),
            Address.amenity.in_(tags)
        ]

        answer = self.session.query(Address).filter(and_(*query_filters)).all()
        answer = [Point.address_to_point(a) for a in answer]

        if 'art_object' in tags:
            art_objects = self.session.query(ArtObject).filter(
                and_(ArtObject.lon.between(min_lon, max_lon),
                ArtObject.lat.between(min_lat, max_lat))
            ).all()
            art_objects = [Point.art_object_to_point(a) for a in art_objects]
            answer.extend(art_objects)

        return answer
