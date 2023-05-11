from src.models.models import GeometryObject, Coordinate
from tests.conftest import TestState


def test_model_repr(state: TestState):
    point = GeometryObject(type="Point", coordinates=[Coordinate(x=1, y=2)])
    state.conn.add(point)
    state.conn.commit()
    state.conn.refresh(point)
    assert repr(point) == "GeometryObject(id=1, type='Point')"
    assert repr(point.coordinates) == "[Coordinate(geometry_object_id=1, id=1, x=1.0, y=2.0)]"
