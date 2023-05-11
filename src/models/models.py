from enum import Enum
from typing import Any

from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.sql.schema import Column

from src.db.database import Base


class GeometryTypes(Enum):
    CONTOUR = "Contour"
    POINT = "Point"


class GeometryObject(Base):
    __tablename__ = "geometry_object"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    type: str = Column(String)
    coordinates: Mapped[list["Coordinate"]] = relationship(
        "Coordinate", cascade="all,delete", backref="geometry_object"
    )

    def to_json(self) -> dict[str, Any]:
        data = {"type": self.type, "coordinates": [[c.x, c.y] for c in self.coordinates]}
        return {"id": self.id, "data": data} if self.id else data


class Coordinate(Base):
    __tablename__ = "coordinate"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    geometry_object_id: int = Column(Integer, ForeignKey("geometry_object.id"))
    x: float = Column(Float, nullable=False)  # type: ignore
    y: float = Column(Float, nullable=False)  # type: ignore
