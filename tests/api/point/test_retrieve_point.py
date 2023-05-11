from tests.conftest import TestState, ValidationError, assert_response, assert_validation_err, client


def test_retrieve_point(state: TestState):
    point = state.create_point([1, 1])
    state.save_points(point)
    response = client.get(f'/points/{point["id"]}')
    assert_response(response, 200, point)


def test_retrieve_point__point_not_found():
    fake_point_id = 999
    response = client.get(f"/points/{fake_point_id}")
    assert_response(response, 404, {"detail": f"Point with an id of {fake_point_id} not found."})


def test_retrieve_point__use_contour_id(state: TestState):
    contour = state.create_contour([[0, 0], [0, 1], [1, 1], [1, 0]])
    state.save_contours(contour)
    response = client.get(f'/points/{contour["id"]}')
    assert_response(response, 404, {"detail": f'Point with an id of {contour["id"]} not found.'})


def test_retrieve_point__invalid_id():
    response = client.get("/points/test")
    err = ValidationError(["path", "point_id"], "value is not a valid integer", "type_error.integer")
    assert_validation_err(response, err)
