from tests.conftest import TestState, ValidationError, assert_response, assert_validation_err, client


def test_delete_point(state: TestState):
    point = state.create_point([1, 1])
    state.save_points(point)
    response = client.delete(f'/points/{point["id"]}')
    assert_response(response, 200, point)
    assert state.get_geometry_object(point["id"]) == {}


def test_delete_point__multiple(state: TestState):
    point_1, point_2 = state.create_point([1, 1]), state.create_point([2.1, 2.1])
    state.save_points(point_1, point_2)
    response = client.delete(f'/points/{point_2["id"]}')
    assert_response(response, 200, point_2)
    assert state.get_geometry_object(point_1["id"]) == point_1
    assert state.get_geometry_object(point_2["id"]) == {}


def test_delete_point__invalid_point():
    response = client.delete("/points/invalid")
    err = ValidationError(["path", "point_id"], "value is not a valid integer", "type_error.integer")
    assert_validation_err(response, err)


def test_delete_point__contour(state: TestState):
    contour = state.create_contour([[0, 0], [0, 1], [1, 1], [1, 0]])
    state.save_contours(contour)
    response = client.delete(f'/points/{contour["id"]}')
    assert_response(response, 404, {"detail": f'Point with an id of {contour["id"]} not found.'})
    assert state.get_geometry_object(contour["id"]) == contour


def test_delete_point__point_not_found():
    fake_point_id = 999
    response = client.delete(f"/points/{fake_point_id}")
    assert_response(response, 404, {"detail": f"Point with an id of {fake_point_id} not found."})
