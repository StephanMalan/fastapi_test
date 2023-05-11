from typing import Annotated, Literal

from pydantic import BaseModel, Extra, Field, ValidationError, validator
from pydantic.error_wrappers import ErrorWrapper
from shapely.geometry import Polygon


class NotFoundModel(BaseModel):
    detail: Annotated[str, Field(..., example="*Item* with an id of x not found.")]


class ContourDataModel(BaseModel, extra=Extra.forbid, orm_mode=True):
    type: Literal["Contour"]
    coordinates: list[tuple[float, float]] = Field(
        min_items=4, example=[[30.01, 10.01], [40.02, 40.02], [20.03, 40.03], [10.04, 20.04]]
    )

    @validator("coordinates")
    @classmethod
    def validate_contour(cls, value: list[tuple[float, float]]) -> list[tuple[float, float]]:
        poly = Polygon(value)
        errors = []
        if not poly.is_valid or not poly.is_simple:
            errors.append(ErrorWrapper(ValueError("contour is not a simple polygon."), (0,)))
        if value[0] != value[-1]:
            errors.append(ErrorWrapper(ValueError("contour is not closed."), (0,)))
        if errors:
            raise ValidationError(errors, ContourDataModel)
        return value

    @validator("coordinates", each_item=True)
    @classmethod
    def validate_coordinates(cls, value: tuple[float, float]) -> tuple[float, float]:
        errors = []
        if not -180 <= value[0] <= 180:
            errors.append(ErrorWrapper(ValueError("x value needs to be between -180 and 180 (inclusive)."), (0,)))
        if not -90 <= value[1] <= 90:
            errors.append(ErrorWrapper(ValueError("y value needs to be between -90 and 90 (inclusive)."), (1,)))
        if errors:
            raise ValidationError(errors, ContourDataModel)
        return value


class ContourResponseModel(BaseModel, orm_mode=True):
    id: int = Field(example=1)
    data: ContourDataModel


class ContourRequestModel(BaseModel, extra=Extra.forbid):
    data: ContourDataModel


class PointDataModel(BaseModel, extra=Extra.forbid, orm_mode=True):
    type: Literal["Point"]
    coordinates: list[tuple[float, float]] = Field(min_items=1, max_items=1, example=[[30.01, 10.01]])

    @validator("coordinates", each_item=True)
    @classmethod
    def validate_coordinates(cls, value: tuple[float, float]) -> tuple[float, float]:
        errors = []
        if not -180 <= value[0] <= 180:
            errors.append(ErrorWrapper(ValueError("x value needs to be between -180 and 180 (inclusive)."), (0,)))
        if not -90 <= value[1] <= 90:
            errors.append(ErrorWrapper(ValueError("y value needs to be between -90 and 90 (inclusive)."), (1,)))
        if errors:
            raise ValidationError(errors, ContourDataModel)
        return value


class PointResponseModel(BaseModel, orm_mode=True):
    id: int = Field(example=1)
    data: PointDataModel


class PointRequestModel(BaseModel, extra=Extra.forbid):
    data: PointDataModel
