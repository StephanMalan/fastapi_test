# from shapely.geometry.base import BaseGeometry
class Geom:
    geoms: list["Geom"]
    geom_type: str
    exterior: "Polygon"

class Polygon(Geom):
    is_valid: bool
    is_simple: bool
    coords: list[tuple[float, float]]
    def __init__(self, _point: list[tuple[float, float]]) -> None: ...
    def intersects(self, _point: "Point") -> bool: ...
    def intersection(self, _poly: "Polygon") -> Geom: ...

class Point(Geom):
    def __init__(self, _x: float, _y: float) -> None: ...
