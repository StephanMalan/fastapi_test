from tests.conftest import TestState, ValidationError, assert_response, assert_validation_err, client


def test_retrieve_points(state: TestState):
    point_1, point_2 = state.create_point([1.0, 1.0]), state.create_point([2.2, 2.2])
    state.save_points(point_1, point_2)
    response = client.get("/points")
    assert_response(response, 200, [point_1, point_2])


def test_retrieve_points__single_point(state: TestState):
    point = state.create_point([1.0, 1.0])
    state.save_points(point)
    response = client.get("/points")
    assert_response(response, 200, [point])


def test_retrieve_points__no_points(state: TestState):
    state.clear_all_tables()
    response = client.get("/points")
    assert_response(response, 200, [])


def test_retrieve_points__only_contours(state: TestState):
    contour = state.create_contour([[0.5, 0.5], [0.5, 1.5], [1.5, 1.5], [1.5, 0.5]])
    state.save_contours(contour)
    response = client.get("/points")
    assert_response(response, 200, [])


def test_retrieve_points__limit_result(state: TestState):
    point_1, point_2 = state.create_point([1.0, 1.0]), state.create_point([2.2, 2.2])
    state.save_points(point_1, point_2)
    response = client.get("/points", params={"limit": 1})
    assert_response(response, 200, [point_1])


def test_retrieve_points__invalid_limit():
    response = client.get("/points", params={"limit": "invalid"})
    err = ValidationError(["query", "limit"], "value is not a valid integer", "type_error.integer")
    assert_validation_err(response, err)


def test_retrieve_points__offset_result(state: TestState):
    p_1, p_2, p_3 = state.create_point([1.0, 1.0]), state.create_point([2.2, 2.2]), state.create_point([3.4, 3.9])
    state.save_points(p_1, p_2, p_3)
    response = client.get("/points", params={"offset": 1})
    assert_response(response, 200, [p_2, p_3])


def test_retrieve_points__invalid_offset():
    response = client.get("/points", params={"offset": "invalid"})
    err = ValidationError(["query", "offset"], "value is not a valid integer", "type_error.integer")
    assert_validation_err(response, err)


def test_retrieve_points__limit_and_offset_result(state: TestState):
    p_1, p_2, p_3 = state.create_point([1.0, 1.0]), state.create_point([2.2, 2.2]), state.create_point([3.4, 3.9])
    state.save_points(p_1, p_2, p_3)
    response = client.get("/points", params={"limit": 1, "offset": 1})
    assert_response(response, 200, [p_2])


def test_retrieve_points__within_contour(state: TestState):
    point_1, point_2 = state.create_point([1.0, 1.0]), state.create_point([2.2, 2.2])
    state.save_points(point_1, point_2)
    contour = state.create_contour([[0.5, 0.5], [0.5, 1.5], [1.5, 1.5], [1.5, 0.5]])
    state.save_contours(contour)
    response = client.get("/points", params={"contour_id": contour["id"]})
    assert_response(response, 200, [point_1])


def test_retrieve_points__within_invalid_contour():
    response = client.get("/points", params={"contour_id": "invalid"})
    err = ValidationError(["query", "contour_id"], "value is not a valid integer", "type_error.integer")
    assert_validation_err(response, err)


def test_retrieve_points__multiple_within_contour(state: TestState):
    point_1, point_2 = state.create_point([1.0, 1.0]), state.create_point([2.2, 2.2])
    state.save_points(point_1, point_2)
    contour = state.create_contour([[0, 0], [0, 10], [10, 10], [10, 0]])
    state.save_contours(contour)
    response = client.get("/points", params={"contour_id": contour["id"]})
    assert_response(response, 200, [point_1, point_2])


def test_retrieve_points__none_within_contour(state: TestState):
    point_1, point_2 = state.create_point([1.0, 1.0]), state.create_point([2.2, 2.2])
    state.save_points(point_1, point_2)
    contour = state.create_contour([[-0.5, -0.5], [-0.5, -1.5], [-1.5, -1.5], [-1.5, -0.5]])
    state.save_contours(contour)
    response = client.get("/points", params={"contour_id": contour["id"]})
    assert_response(response, 200, [])


def test_retrieve_points__within_contour_not_found():
    fake_contour_id = 999
    response = client.get("/points", params={"contour_id": 999})
    assert_response(response, 404, {"detail": f"Contour with an id of {fake_contour_id} not found."})
