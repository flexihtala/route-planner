import math


class PlaneCoordinates:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def get_distance_to(self, other) -> float:
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def get_length(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)
