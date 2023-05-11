from dataclasses import dataclass
from typing import Any, Generator, Optional

import pytest
from fastapi.testclient import TestClient
from httpx import Response
from sqlalchemy.orm import Session
from sqlalchemy.sql import text as sa_text

from src.api.main import app
from src.db.database import get_db_session
from src.models.models import Coordinate, GeometryObject

client = TestClient(app)


@pytest.fixture
def state() -> Generator["TestState", None, None]:
    test_state = TestState()
    yield test_state
    test_state.clean_up()


class TestState:
    __test__ = False

    def __init__(self) -> None:
        self.conn = self._get_connection()
        self.clear_all_tables()
        self._id = 1

    def _get_connection(self) -> Session:
        return next(get_db_session())

    def _get_next_id(self) -> int:
        next_id = self._id
        self._id += 1
        return next_id

    def clean_up(self) -> None:
        self.conn.close()

    def clear_all_tables(self) -> None:
        self.conn.execute(sa_text("TRUNCATE coordinate, geometry_object RESTART IDENTITY"))
        self.conn.commit()

    def create_point(self, coordinates: list[float], id: int | None = None) -> dict[str, Any]:
        return {"id": id if id else self._get_next_id(), "data": {"type": "Point", "coordinates": [coordinates]}}

    def create_contour(self, coordinates: list[list[float]], id: int | None = None) -> dict[str, Any]:
        return {"id": id if id else self._get_next_id(), "data": {"type": "Contour", "coordinates": coordinates}}

    def save_points(self, *point_data: dict[str, Any]) -> None:
        self._save_objects("Point", point_data)

    def save_contours(self, *contour_data: dict[str, Any]) -> None:
        self._save_objects("Contour", contour_data)

    def _save_objects(self, type: str, obj_data: tuple[dict[str, Any], ...]) -> None:
        objects = [
            GeometryObject(type=type, coordinates=[Coordinate(x=c[0], y=c[1]) for c in p["data"]["coordinates"]])
            for p in obj_data
        ]
        self.conn.add_all(objects)
        self.conn.commit()

    def get_geometry_object(self, object_id: int) -> dict[str, Any]:
        output = self.conn.query(GeometryObject).filter(GeometryObject.id == object_id).first()
        return output.to_json() if output else {}


@dataclass
class ValidationError:
    loc: list[Any]
    msg: str
    type: str
    ctx: Optional[dict[str, Any]] = None

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if v}


def assert_response(response: Response, result_code: int, response_json: dict[str, Any] | list[dict[str, Any]]) -> None:
    assert response.status_code == result_code
    assert response.json() == response_json


def assert_validation_err(
    response: Response, validation_err: list[ValidationError] | ValidationError, result_code: int = 422
) -> None:
    detail = [e.to_dict() for e in validation_err] if isinstance(validation_err, list) else [validation_err.to_dict()]
    assert response.status_code == result_code
    assert response.json() == {"detail": detail}
