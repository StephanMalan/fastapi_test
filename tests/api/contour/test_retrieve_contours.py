from tests.conftest import TestState, ValidationError, assert_response, assert_validation_err, client


def test_retrieve_contours(state: TestState):
    contours_1 = state.create_contour([[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]])
    contours_2 = state.create_contour([[0, 0], [0, 2], [2, 2], [2, 0], [0, 0]])
    state.save_contours(contours_1, contours_2)
    response = client.get("/contours")
    assert_response(response, 200, [contours_1, contours_2])


def test_retrieve_contours__single_contour(state: TestState):
    contour = state.create_contour([[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]])
    state.save_contours(contour)
    response = client.get("/contours")
    assert_response(response, 200, [contour])


def test_retrieve_contours__no_contours(state: TestState):
    state.clear_all_tables()
    response = client.get("/contours")
    assert_response(response, 200, [])


def test_retrieve_contours__only_points(state: TestState):
    point = state.create_point([0.5, 0.5])
    state.save_points(point)
    response = client.get("/contours")
    assert_response(response, 200, [])


def test_retrieve_contours__limit_result(state: TestState):
    contours_1 = state.create_contour([[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]])
    contours_2 = state.create_contour([[0, 0], [0, 2], [2, 2], [2, 0], [0, 0]])
    state.save_contours(contours_1, contours_2)
    response = client.get("/contours", params={"limit": 1})
    assert_response(response, 200, [contours_1])


def test_retrieve_contours__invalid_limit():
    response = client.get("/contours", params={"limit": "invalid"})
    err = ValidationError(["query", "limit"], "value is not a valid integer", "type_error.integer")
    assert_validation_err(response, err)


def test_retrieve_contours__offset_result(state: TestState):
    contours_1 = state.create_contour([[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]])
    contours_2 = state.create_contour([[0, 0], [0, 2], [2, 2], [2, 0], [0, 0]])
    contours_3 = state.create_contour([[0, 0], [0, 3], [3, 3], [3, 0], [0, 0]])
    state.save_contours(contours_1, contours_2, contours_3)
    response = client.get("/contours", params={"offset": 1})
    assert_response(response, 200, [contours_2, contours_3])


def test_retrieve_contours__invalid_offset():
    response = client.get("/contours", params={"offset": "invalid"})
    err = ValidationError(["query", "offset"], "value is not a valid integer", "type_error.integer")
    assert_validation_err(response, err)


def test_retrieve_contours__limit_and_offset_result(state: TestState):
    contours_1 = state.create_contour([[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]])
    contours_2 = state.create_contour([[0, 0], [0, 2], [2, 2], [2, 0], [0, 0]])
    contours_3 = state.create_contour([[0, 0], [0, 3], [3, 3], [3, 0], [0, 0]])
    state.save_contours(contours_1, contours_2, contours_3)
    response = client.get("/contours", params={"limit": 1, "offset": 1})
    assert_response(response, 200, [contours_2])
