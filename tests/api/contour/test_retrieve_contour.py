from tests.conftest import TestState, ValidationError, assert_response, assert_validation_err, client


def test_retrieve_contour(state: TestState):
    contour = state.create_contour([[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]])
    state.save_contours(contour)
    response = client.get(f'/contours/{contour["id"]}')
    assert_response(response, 200, contour)


def test_retrieve_contour__contour_not_found():
    fake_contour_id = 999
    response = client.get(f"/contours/{fake_contour_id}")
    assert_response(response, 404, {"detail": f"Contour with an id of {fake_contour_id} not found."})


def test_retrieve_contour__use_point_id(state: TestState):
    point = state.create_point([0, 0])
    state.save_points(point)
    response = client.get(f'/contours/{point["id"]}')
    assert_response(response, 404, {"detail": f'Contour with an id of {point["id"]} not found.'})


def test_retrieve_contour__invalid_id():
    response = client.get("/contours/test")
    err = ValidationError(["path", "contour_id"], "value is not a valid integer", "type_error.integer")
    assert_validation_err(response, err)


def test_retrieve_contour_intersections(state: TestState):
    contour_1 = state.create_contour([[1, 0], [1, 1], [2, 1], [2, 2], [1, 2], [1, 3], [3, 3], [3, 0]])
    contour_2 = state.create_contour([[0, 0], [2, 0], [2, 1], [1, 1], [1, 3], [0, 3]])
    state.save_contours(contour_1, contour_2)
    response = client.get(f'/contours/{contour_1["id"]}/intersections', params={"contour": contour_2["id"]})
    print(response.json())
    json_data = [{"type": "Contour", "coordinates": [[1, 1], [2, 1], [2, 0], [1, 0], [1, 1]]}]
    assert_response(response, 200, json_data)


def test_retrieve_contour_intersections__multiple(state: TestState):
    contour_1 = state.create_contour([[1, 0], [1, 1], [2, 1], [2, 2], [1, 2], [1, 3], [3, 3], [3, 0]])
    contour_2 = state.create_contour([[0, 0], [0, 3], [2, 3], [2, 2], [1, 2], [1, 1], [2, 1], [2, 0]])
    state.save_contours(contour_1, contour_2)
    response = client.get(f'/contours/{contour_1["id"]}/intersections', params={"contour": contour_2["id"]})
    print(response.json())
    json_data = [
        {"type": "Contour", "coordinates": [[1, 1], [2, 1], [2, 0], [1, 0], [1, 1]]},
        {"type": "Contour", "coordinates": [[1, 2], [1, 3], [2, 3], [2, 2], [1, 2]]},
    ]
    assert_response(response, 200, json_data)


def test_retrieve_contour_intersections__none(state: TestState):
    contour_1 = state.create_contour([[1, 0], [1, 1], [2, 1], [2, 2], [1, 2], [1, 3], [3, 3], [3, 0]])
    contour_2 = state.create_contour([[0, 0], [0, 3], [1, 3], [1, 0]])
    state.save_contours(contour_1, contour_2)
    response = client.get(f'/contours/{contour_1["id"]}/intersections', params={"contour": contour_2["id"]})
    print(response.json())
    json_data = {"detail": f'No intersection between contours {contour_1["id"]} and {contour_2["id"]}.'}
    assert_response(response, 404, json_data)


def test_retrieve_contour_intersections__contours_not_found(state: TestState):
    contour = state.create_contour([[1, 0], [1, 1], [2, 1], [2, 2], [1, 2], [1, 3], [3, 3], [3, 0]])
    state.save_contours(contour)
    fake_contour_id = 999

    response = client.get(f'/contours/{contour["id"]}/intersections', params={"contour": fake_contour_id})
    print(response.json())
    assert_response(response, 404, {"detail": f"Contour with an id of {fake_contour_id} not found."})

    response = client.get(f"/contours/{fake_contour_id}/intersections", params={"contour": contour["id"]})
    assert_response(response, 404, {"detail": f"Contour with an id of {fake_contour_id} not found."})


def test_retrieve_contour_intersections__using_point(state: TestState):
    contour = state.create_contour([[1, 0], [1, 1], [2, 1], [2, 2], [1, 2], [1, 3], [3, 3], [3, 0]])
    state.save_contours(contour)
    point = state.create_point([1, 0])
    state.save_points(point)

    response = client.get(f'/contours/{point["id"]}/intersections', params={"contour": contour["id"]})
    print(response.json())
    assert_response(response, 404, {"detail": f'Contour with an id of {point["id"]} not found.'})

    response = client.get(f'/contours/{contour["id"]}/intersections', params={"contour": point["id"]})
    assert_response(response, 404, {"detail": f'Contour with an id of {point["id"]} not found.'})


def test_retrieve_contour_intersections__invalid_contour(state: TestState):
    contour = state.create_contour([[1, 0], [1, 1], [2, 1], [2, 2], [1, 2], [1, 3], [3, 3], [3, 0]])
    state.save_contours(contour)

    response = client.get("/contours/invalid/intersections", params={"contour": contour["id"]})
    print("ID:", contour["id"])
    err = ValidationError(["path", "contour_id"], "value is not a valid integer", "type_error.integer")
    assert_validation_err(response, err)

    response = client.get(f'/contours/{contour["id"]}/intersections', params={"contour": "invalid"})
    err = ValidationError(["query", "contour"], "value is not a valid integer", "type_error.integer")
    assert_validation_err(response, err)
