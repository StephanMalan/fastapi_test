from tests.conftest import TestState, ValidationError, assert_response, assert_validation_err, client


def test_update_contour(state: TestState):
    contour = state.create_contour([[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]])
    state.save_contours(contour)
    new_contour = state.create_contour([[0, 0], [0, 2], [2, 2], [2, 0], [0, 0]], id=contour["id"])
    response = client.patch(f'/contours/{contour["id"]}', json={"data": new_contour["data"]})
    assert_response(response, 200, new_contour)
    assert state.get_geometry_object(contour["id"]) == new_contour


def test_update_contour__coord_bounds(state: TestState):
    contour = state.create_contour([[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]])
    state.save_contours(contour)
    new_contour = state.create_contour([[-180, -90], [-180, 90], [180, 90], [180, -90], [-180, -90]], id=contour["id"])
    response = client.patch(f'/contours/{contour["id"]}', json={"data": new_contour["data"]})
    assert_response(response, 200, new_contour)
    assert state.get_geometry_object(contour["id"]) == new_contour


def test_update_contour__contour_not_found(state: TestState):
    fake_contour_id = 999
    new_contour = state.create_contour([[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]])
    response = client.patch(f"/contours/{fake_contour_id}", json={"data": new_contour["data"]})
    assert_response(response, 404, {"detail": f"Contour with an id of {fake_contour_id} not found."})


def test_update_contour__point(state: TestState):
    point = state.create_point([0.0, 0.0])
    state.save_points(point)
    new_contour = state.create_contour([[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]], id=point["id"])
    response = client.patch(f'/contours/{point["id"]}', json={"data": new_contour["data"]})
    assert_response(response, 404, {"detail": f'Contour with an id of {point["id"]} not found.'})
    assert state.get_geometry_object(point["id"]) == point


def test_update_contour__invalid_contour(state: TestState):
    new_contour = state.create_contour([[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]])
    response = client.patch("/contours/invalid", json={"data": new_contour["data"]})
    err = ValidationError(["path", "contour_id"], "value is not a valid integer", "type_error.integer")
    assert_validation_err(response, err)


def test_update_contour__extra_fields(state: TestState):
    contour = state.create_contour([[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]])
    state.save_contours(contour)
    msg, err_type = "extra fields not permitted", "value_error.extra"

    json_data = {"extra": "field", "data": {"type": "Contour", "coordinates": [[0, 0], [0, 2], [2, 2], [2, 0], [0, 0]]}}
    resp = client.patch(f'/contours/{contour["id"]}', json=json_data)
    assert_validation_err(resp, ValidationError(["body", "extra"], msg, err_type))

    json_data = {"data": {"extra": "field", "type": "Contour", "coordinates": [[0, 0], [0, 2], [2, 2], [2, 0], [0, 0]]}}
    resp = client.patch(f'/contours/{contour["id"]}', json=json_data)
    assert_validation_err(resp, ValidationError(["body", "data", "extra"], msg, err_type))

    json_data = {"data": {"type": "Contour", "coordinates": [[0, 0], [0, 2], [2, 2], [2, 0], [0, 0], "extra"]}}
    resp = client.patch(f'/contours/{contour["id"]}', json=json_data)
    msg, err_type = "value is not a valid tuple", "type_error.tuple"
    assert_validation_err(resp, ValidationError(["body", "data", "coordinates", 5], msg, err_type))

    assert state.get_geometry_object(contour["id"]) == contour


def test_update_contour__invalid_type(state: TestState):
    contour = state.create_contour([[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]])
    state.save_contours(contour)
    json_data = {"data": {"type": "Invalid", "coordinates": [[0, 0], [0, 2], [2, 2], [2, 0], [0, 0]]}}
    response = client.patch(f'/contours/{contour["id"]}', json=json_data)
    ctx = {"given": "Invalid", "permitted": ["Contour"]}
    msg, err_type = "unexpected value; permitted: 'Contour'", "value_error.const"
    assert_validation_err(response, ValidationError(["body", "data", "type"], msg, err_type, ctx=ctx))
    assert state.get_geometry_object(contour["id"]) == contour


def test_update_contour__not_2d_coord(state: TestState):
    contour = state.create_contour([[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]])
    state.save_contours(contour)
    json_data = {"data": {"type": "Contour", "coordinates": [[0, 0, 0], [2, 2], [0, 2], [2, 0], [0, 0]]}}
    response = client.patch(f'/contours/{contour["id"]}', json=json_data)
    msg, err_type = "wrong tuple length 3, expected 2", "value_error.tuple.length"
    ctx = {"actual_length": 3, "expected_length": 2}
    assert_validation_err(response, ValidationError(["body", "data", "coordinates", 0], msg, err_type, ctx=ctx))
    assert state.get_geometry_object(contour["id"]) == contour


def test_update_contour__too_few_coords(state: TestState):
    contour = state.create_contour([[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]])
    state.save_contours(contour)
    json_data = {"data": {"type": "Contour", "coordinates": []}}
    response = client.patch(f'/contours/{contour["id"]}', json=json_data)
    msg, err_type = "ensure this value has at least 4 items", "value_error.list.min_items"
    ctx = {"limit_value": 4}
    assert_validation_err(response, ValidationError(["body", "data", "coordinates"], msg, err_type, ctx=ctx))
    assert state.get_geometry_object(contour["id"]) == contour


def test_update_contour__single_set_coords(state: TestState):
    contour = state.create_contour([[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]])
    state.save_contours(contour)
    json_data = {"data": {"type": "Contour", "coordinates": [1, 1]}}
    response = client.patch(f'/contours/{contour["id"]}', json=json_data)
    msg, err_type = "ensure this value has at least 4 items", "value_error.list.min_items"
    ctx = {"limit_value": 4}
    assert_validation_err(response, ValidationError(["body", "data", "coordinates"], msg, err_type, ctx=ctx))
    assert state.get_geometry_object(contour["id"]) == contour


def test_update_contour__invalid_coords(state: TestState):
    contour = state.create_contour([[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]])
    state.save_contours(contour)
    json_data = {"data": {"type": "Contour", "coordinates": [["invalid", 0], [2, 2], [0, 2], [2, 0], [0, 0]]}}
    response = client.patch(f'/contours/{contour["id"]}', json=json_data)
    msg, err_type = "value is not a valid float", "type_error.float"
    assert_validation_err(response, ValidationError(["body", "data", "coordinates", 0, 0], msg, err_type))
    assert state.get_geometry_object(contour["id"]) == contour


def test_update_contour__outside_coord_bounds(state: TestState):
    contour = state.create_contour([[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]])
    state.save_contours(contour)
    new_contour = state.create_contour([[0, 1], [180.1, 90.1], [1, 0], [-180.1, -90.1], [0, 1]], id=contour["id"])
    response = client.patch(f'/contours/{contour["id"]}', json={"data": new_contour["data"]})
    x_err_msg = "x value needs to be between -180 and 180 (inclusive)."
    y_err_msg = "y value needs to be between -90 and 90 (inclusive)."
    err_1 = ValidationError(["body", "data", "coordinates", 1, 0], x_err_msg, "value_error")
    err_2 = ValidationError(["body", "data", "coordinates", 1, 1], y_err_msg, "value_error")
    err_3 = ValidationError(["body", "data", "coordinates", 3, 0], x_err_msg, "value_error")
    err_4 = ValidationError(["body", "data", "coordinates", 3, 1], y_err_msg, "value_error")
    assert_validation_err(response, [err_1, err_2, err_3, err_4])
    assert state.get_geometry_object(contour["id"]) == contour


def test_update_contour__non_simple_polygon(state: TestState):
    contour = state.create_contour([[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]])
    state.save_contours(contour)
    json_data = {"data": {"type": "Contour", "coordinates": [[0, 0], [1, 1], [1, 0], [0, 1], [0, 0]]}}
    response = client.patch(f'/contours/{contour["id"]}', json=json_data)
    msg, err_type = "contour is not a simple polygon.", "value_error"
    assert_validation_err(response, ValidationError(["body", "data", "coordinates", 0], msg, err_type))


def test_update_contour__not_closed(state: TestState):
    contour = state.create_contour([[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]])
    state.save_contours(contour)
    json_data = {"data": {"type": "Contour", "coordinates": [[0, 0], [0, 2], [2, 2], [2, 0]]}}
    response = client.patch(f'/contours/{contour["id"]}', json=json_data)
    msg, err_type = "contour is not closed.", "value_error"
    assert_validation_err(response, ValidationError(["body", "data", "coordinates", 0], msg, err_type))
