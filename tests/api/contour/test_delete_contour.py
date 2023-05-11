from tests.conftest import TestState, ValidationError, assert_response, assert_validation_err, client


def test_delete_contour(state: TestState):
    contour = state.create_contour([[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]])
    state.save_contours(contour)
    response = client.delete(f'/contours/{contour["id"]}')
    assert_response(response, 200, contour)
    assert state.get_geometry_object(contour["id"]) == {}


def test_delete_contour__multiple(state: TestState):
    contour_1 = state.create_contour([[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]])
    contour_2 = state.create_contour([[0, 0], [0, 2], [2, 2], [2, 0], [0, 0]])
    state.save_contours(contour_1, contour_2)
    response = client.delete(f'/contours/{contour_2["id"]}')
    assert_response(response, 200, contour_2)
    assert state.get_geometry_object(contour_1["id"]) == contour_1
    assert state.get_geometry_object(contour_2["id"]) == {}


def test_delete_contour__invalid_point():
    response = client.delete("/contours/invalid")
    err = ValidationError(["path", "contour_id"], "value is not a valid integer", "type_error.integer")
    assert_validation_err(response, err)


def test_delete_contour__point(state: TestState):
    point = state.create_point([0, 0])
    state.save_points(point)
    response = client.delete(f'/contours/{point["id"]}')
    assert_response(response, 404, {"detail": f'Contour with an id of {point["id"]} not found.'})
    assert state.get_geometry_object(point["id"]) == point


def test_delete_contour__contour_not_found():
    fake_contour_id = 999
    response = client.delete(f"/contours/{fake_contour_id}")
    assert_response(response, 404, {"detail": f"Contour with an id of {fake_contour_id} not found."})
