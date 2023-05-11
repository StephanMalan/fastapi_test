from typing import Any

from fastapi import HTTPException
from shapely.geometry import Polygon
from sqlalchemy.orm import Query, Session

from src.models.models import Coordinate, GeometryObject, GeometryTypes
from src.models.schemas import NotFoundModel

NOT_FOUND_REPSONSE: dict[int | str, dict[str, Any]] | None = {404: {"model": NotFoundModel}}


def create_geometry_object(object_type: GeometryTypes, coords: list[tuple[float, float]]) -> GeometryObject:
    return GeometryObject(type=object_type.value, coordinates=[Coordinate(x=coord[0], y=coord[1]) for coord in coords])


def get_geometry_objects(
    object_type: GeometryTypes, limit: int | None, offset: int | None, db: Session
) -> list[GeometryObject]:
    query: Query[GeometryObject] = db.query(GeometryObject).filter(GeometryObject.type == object_type.value)
    query = query.order_by(GeometryObject.id)
    if limit:
        query = query.limit(limit)
    if offset:
        query = query.offset(offset)
    return query.all()


def get_geometry_object(object_type: GeometryTypes, object_id: int, db: Session) -> GeometryObject:
    filtered: Query[GeometryObject] = db.query(GeometryObject).filter(
        GeometryObject.type == object_type.value, GeometryObject.id == object_id
    )
    output = filtered.first()
    if not output:
        raise HTTPException(404, f"{object_type.value} with an id of {object_id} not found.")
    return output


def get_polygon(contour_id: int, db: Session) -> Polygon:
    contour: GeometryObject = get_geometry_object(GeometryTypes.CONTOUR, contour_id, db)
    return Polygon(list((coord.x, coord.y) for coord in contour.coordinates))


def validate_present(value: Any | None, status_code: int, error_message: str) -> None:
    if not value:
        raise HTTPException(status_code=status_code, detail=error_message)
