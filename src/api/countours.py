from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from src.api import NOT_FOUND_REPSONSE, create_geometry_object, get_geometry_object, get_geometry_objects, get_polygon
from src.db.database import get_db_session
from src.models.models import Coordinate, GeometryTypes
from src.models.schemas import ContourDataModel, ContourRequestModel, ContourResponseModel

CONTOUR = GeometryTypes.CONTOUR

router = router = APIRouter(prefix="/contours", tags=["Contours"])


@router.get("/", description="Allows the user to retrieve all the saved contours.")
def retrieve_contours(
    limit: Annotated[int, Query(ge=1, le=500, description="Specifies the maximum number of items to return.")] = 50,
    offset: Annotated[
        int, Query(ge=0, description="Specifies the number of items to skip before starting to return results.")
    ] = 0,
    db: Session = Depends(get_db_session),
) -> list[ContourResponseModel]:
    return [ContourResponseModel(**v.to_json()) for v in get_geometry_objects(CONTOUR, limit, offset, db)]


@router.get("/{contour_id}", description="Allows the user to request a specific contour.", responses=NOT_FOUND_REPSONSE)
def retrieve_contour(
    contour_id: Annotated[int, Path(..., ge=1, description="ID of the contour to retrieve")],
    db: Session = Depends(get_db_session),
) -> ContourResponseModel:
    return ContourResponseModel(**get_geometry_object(CONTOUR, contour_id, db).to_json())


@router.get(
    "/{contour_id}/intersections",
    description="Allows the user to calculate the contours formed within the intersection of two other contours.",
    responses=NOT_FOUND_REPSONSE,
)
def retrieve_contour_intersection(
    contour_id: Annotated[int, Path(..., ge=1, description="First contour id to calculate intersection with.")],
    contour: Annotated[int, Query(..., ge=1, description="Second contour id to calculate intersection with.")],
    db: Session = Depends(get_db_session),
) -> list[ContourDataModel]:
    intersect = get_polygon(contour_id, db).intersection(get_polygon(contour, db))
    geoms = list(intersect.geoms) if intersect.geom_type in ["MultiPolygon", "GeometryCollection"] else [intersect]
    polygons = [geom for geom in geoms if geom.geom_type == "Polygon"]
    if not polygons:
        raise HTTPException(status_code=404, detail=f"No intersection between contours {contour_id} and {contour}.")

    contours = [create_geometry_object(CONTOUR, poly.exterior.coords) for poly in polygons]
    return [ContourDataModel(**cont.to_json()) for cont in contours]


@router.post("/", description="Allows the user to add a new contour.")
def create_contour(request: ContourRequestModel, db: Session = Depends(get_db_session)) -> ContourResponseModel:
    new_contour = create_geometry_object(CONTOUR, request.data.coordinates)
    db.add(new_contour)
    db.commit()
    db.refresh(new_contour)
    return ContourResponseModel(**new_contour.to_json())


@router.patch(
    "/{contour_id}", description="Allows the user to update a specific contour.", responses=NOT_FOUND_REPSONSE
)
def update_contour(
    request: ContourRequestModel,
    contour_id: Annotated[int, Path(..., ge=1, description="ID of the contour to update.")],
    db: Session = Depends(get_db_session),
) -> ContourResponseModel:
    cont_to_update = get_geometry_object(CONTOUR, contour_id, db)
    cont_to_update.coordinates = [Coordinate(x=coord[0], y=coord[1]) for coord in request.data.coordinates]
    db.commit()
    return ContourResponseModel(**cont_to_update.to_json())


@router.delete(
    "/{contour_id}", description="Allows the user to delete a specific contour.", responses=NOT_FOUND_REPSONSE
)
def delete_contour(
    contour_id: Annotated[int, Path(..., ge=1, description="ID of the contour to delete.")],
    db: Session = Depends(get_db_session),
) -> ContourResponseModel:
    cont_to_delete = get_geometry_object(CONTOUR, contour_id, db)
    db.delete(cont_to_delete)
    db.commit()
    return ContourResponseModel(**cont_to_delete.to_json())
