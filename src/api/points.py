from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query
from shapely.geometry import Point
from sqlalchemy.orm import Session

from src.api import NOT_FOUND_REPSONSE, create_geometry_object, get_geometry_object, get_geometry_objects, get_polygon
from src.db.database import get_db_session
from src.models.models import Coordinate, GeometryTypes
from src.models.schemas import PointRequestModel, PointResponseModel

POINT = GeometryTypes.POINT
router = APIRouter(prefix="/points", tags=["Points"])


@router.get("/", description="Allows the user to retrieve all the saved points.")
def retrieve_points(
    contour_id: Annotated[
        int | None,
        Query(ge=1, description="When set to a valid contour id, it will only return points within that contour."),
    ] = None,
    limit: Annotated[int, Query(ge=1, le=500, description="Specifies the maximum number of items to return.")] = 50,
    offset: Annotated[
        int, Query(ge=0, description="Specifies the number of items to skip before starting to return results.")
    ] = 0,
    db: Session = Depends(get_db_session),
) -> list[PointResponseModel]:
    if contour_id is None:
        return [PointResponseModel(**p.to_json()) for p in get_geometry_objects(POINT, limit, offset, db)]

    poly = get_polygon(contour_id, db)
    points = get_geometry_objects(POINT, None, None, db)
    points = [p for p in points if poly.intersects(Point(p.coordinates[0].x, p.coordinates[0].y))]
    return [PointResponseModel(**p.to_json()) for p in points]


@router.get("/{point_id}", description="Allows the user to request a specific point.", responses=NOT_FOUND_REPSONSE)
def retrieve_point(
    point_id: Annotated[int, Path(..., ge=1, description="ID of the point to retrieve.")],
    db: Session = Depends(get_db_session),
) -> PointResponseModel:
    return PointResponseModel(**get_geometry_object(POINT, point_id, db).to_json())


@router.post("/", description="Allows the user to add a new point.")
def create_point(request: PointRequestModel, db: Session = Depends(get_db_session)) -> PointResponseModel:
    new_point = create_geometry_object(POINT, request.data.coordinates)
    db.add(new_point)
    db.commit()
    db.refresh(new_point)
    return PointResponseModel(**new_point.to_json())


@router.patch("/{point_id}", description="Allows the user to update a specific point.", responses=NOT_FOUND_REPSONSE)
def update_point(
    request: PointRequestModel,
    point_id: Annotated[int, Path(..., ge=1, description="ID of the point to delete.")],
    db: Session = Depends(get_db_session),
) -> PointResponseModel:
    point_to_update = get_geometry_object(POINT, point_id, db)
    point_to_update.coordinates = [Coordinate(x=coord[0], y=coord[1]) for coord in request.data.coordinates]
    db.commit()
    return PointResponseModel(**point_to_update.to_json())


@router.delete("/{point_id}", description="Allows the user to delete a specific point.", responses=NOT_FOUND_REPSONSE)
def delete_point(
    point_id: Annotated[int, Path(..., ge=1, description="ID of the point to delete.")],
    db: Session = Depends(get_db_session),
) -> PointResponseModel:
    point_to_delete = get_geometry_object(POINT, point_id, db)
    db.delete(point_to_delete)
    db.commit()
    return PointResponseModel(**point_to_delete.to_json())
