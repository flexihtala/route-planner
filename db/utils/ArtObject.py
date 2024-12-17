from sqlalchemy import Column, Float, String, Integer, JSON
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class ArtObject(Base):
    __tablename__ = 'artobjects'

    id = Column(Integer, primary_key=True)
    lon: Column = Column(Float, nullable=False)
    lat: Column = Column(Float, nullable=False)
    name = Column(String, nullable=False)
    amenity = 'art_object'
    category = Column(String, nullable=False)
