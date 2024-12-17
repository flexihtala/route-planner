from sqlalchemy import Column, Float, String, Integer, JSON
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Address(Base):
    __tablename__ = 'objects'

    id = Column(Integer, primary_key=True)
    lon: Column = Column(Float, nullable=False)
    lat: Column = Column(Float, nullable=False)
    street = Column(String, nullable=False)
    house = Column(String, nullable=False)
    amenity: Column = Column(String, nullable=False)
    tags = Column(JSON, nullable=False)

    def __str__(self):
        return (f"{self.street}, {self.house} at {self.coordinates.latitude},"
                f" {self.coordinates.longitude}")
