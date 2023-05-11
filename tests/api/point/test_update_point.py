from tests.conftest import TestState, ValidationError, assert_response, assert_validation_err, client


def test_update_point(state: TestState):
    point = state.create_point([1.0, 1.0])
    state.save_points(point)
    new_point = state.create_point([2.1, 2.1], id=point["id"])
    response = client.patch(f'/points/{point["id"]}', json={"data": new_point["data"]})
    assert_response(response, 200, new_point)
    assert state.get_geometry_object(point["id"]) == new_point


def test_update_point__lower_coord_bounds(state: TestState):
    point = state.create_point([1.0, 1.0])
    state.save_points(point)
    new_point = state.create_point([-180, -90], id=point["id"])
    response = client.patch(f'/points/{point["id"]}', json={"data": new_point["data"]})
    assert_response(response, 200, new_point)
    assert state.get_geometry_object(point["id"]) == new_point


def test_update_point__upper_coord_bounds(state: TestState):
    point = state.create_point([1.0, 1.0])
    state.save_points(point)
    new_point = state.create_point([180, 90], id=point["id"])
    response = client.patch(f'/points/{point["id"]}', json={"data": new_point["data"]})
    assert_response(response, 200, new_point)
    assert state.get_geometry_object(point["id"]) == new_point


def test_update_point__point_not_found(state: TestState):
    fake_point_id = 999
    new_point = state.create_point([1, 1])
    response = client.patch(f"/points/{fake_point_id}", json={"data": new_point["data"]})
    assert_response(response, 404, {"detail": f"Point with an id of {fake_point_id} not found."})


def test_update_point__contour(state: TestState):
    contour = state.create_contour([[0.0, 0.0], [0.0, 1.0], [1.0, 1.0], [1.0, 0.0]])
    state.save_contours(contour)
    new_point = state.create_point([180, 90], id=contour["id"])
    response = client.patch(f'/points/{contour["id"]}', json={"data": new_point["data"]})
    assert_response(response, 404, {"detail": f'Point with an id of {contour["id"]} not found.'})
    assert state.get_geometry_object(contour["id"]) == contour


def test_update_point__invalid_point(state: TestState):
    new_point = state.create_point([1, 1])
    response = client.patch("/points/invalid", json={"data": new_point["data"]})
    err = ValidationError(["path", "point_id"], "value is not a valid integer", "type_error.integer")
    assert_validation_err(response, err)


def test_update_point__extra_fields(state: TestState):
    point = state.create_point([1.0, 1.0])
    state.save_points(point)
    msg, err_type = "extra fields not permitted", "value_error.extra"

    json_data = {"extra": "field", "data": {"type": "Point", "coordinates": [[1, 1]]}}
    resp = client.patch(f'/points/{point["id"]}', json=json_data)
    assert_validation_err(resp, ValidationError(["body", "extra"], msg, err_type))

    json_data = {"data": {"extra": "field", "type": "Point", "coordinates": [[1, 1]]}}
    resp = client.patch(f'/points/{point["id"]}', json=json_data)
    assert_validation_err(resp, ValidationError(["body", "data", "extra"], msg, err_type))

    json_data = {"data": {"type": "Point", "coordinates": [[1, 1], "extra"]}}
    resp = client.patch(f'/points/{point["id"]}', json=json_data)
    msg, err_type = "ensure this value has at most 1 items", "value_error.list.max_items"
    ctx = {"limit_value": 1}
    assert_validation_err(resp, ValidationError(["body", "data", "coordinates"], msg, err_type, ctx=ctx))

    assert state.get_geometry_object(point["id"]) == point


def test_update_point__invalid_type(state: TestState):
    point = state.create_point([1.0, 1.0])
    state.save_points(point)
    json_data = {"data": {"type": "Invalid", "coordinates": [[1, 1]]}}
    response = client.patch(f'/points/{point["id"]}', json=json_data)
    ctx = {"given": "Invalid", "permitted": ["Point"]}
    msg, err_type = "unexpected value; permitted: 'Point'", "value_error.const"
    assert_validation_err(response, ValidationError(["body", "data", "type"], msg, err_type, ctx=ctx))
    assert state.get_geometry_object(point["id"]) == point


def test_update_point__not_2d_coord(state: TestState):
    point = state.create_point([1.0, 1.0])
    state.save_points(point)
    json_data = {"data": {"type": "Point", "coordinates": [[1, 1, 1]]}}
    response = client.patch(f'/points/{point["id"]}', json=json_data)
    msg, err_type = "wrong tuple length 3, expected 2", "value_error.tuple.length"
    ctx = {"actual_length": 3, "expected_length": 2}
    assert_validation_err(response, ValidationError(["body", "data", "coordinates", 0], msg, err_type, ctx=ctx))
    assert state.get_geometry_object(point["id"]) == point


def test_update_point__too_few_coords(state: TestState):
    point = state.create_point([1.0, 1.0])
    state.save_points(point)
    json_data = {"data": {"type": "Point", "coordinates": []}}
    response = client.patch(f'/points/{point["id"]}', json=json_data)
    msg, err_type = "ensure this value has at least 1 items", "value_error.list.min_items"
    ctx = {"limit_value": 1}
    assert_validation_err(response, ValidationError(["body", "data", "coordinates"], msg, err_type, ctx=ctx))
    assert state.get_geometry_object(point["id"]) == point


def test_update_point__too_many_coords(state: TestState):
    point = state.create_point([1.0, 1.0])
    state.save_points(point)
    json_data = {"data": {"type": "Point", "coordinates": [[1, 1], [1, 1]]}}
    response = client.patch(f'/points/{point["id"]}', json=json_data)
    msg, err_type = "ensure this value has at most 1 items", "value_error.list.max_items"
    ctx = {"limit_value": 1}
    assert_validation_err(response, ValidationError(["body", "data", "coordinates"], msg, err_type, ctx=ctx))
    assert state.get_geometry_object(point["id"]) == point


def test_update_point__single_set_coords(state: TestState):
    point = state.create_point([1.0, 1.0])
    state.save_points(point)
    json_data = {"data": {"type": "Point", "coordinates": [1, 1]}}
    response = client.patch(f'/points/{point["id"]}', json=json_data)
    msg, err_type = "ensure this value has at most 1 items", "value_error.list.max_items"
    ctx = {"limit_value": 1}
    assert_validation_err(response, ValidationError(["body", "data", "coordinates"], msg, err_type, ctx=ctx))
    assert state.get_geometry_object(point["id"]) == point


def test_update_point__invalid_coords(state: TestState):
    point = state.create_point([1.0, 1.0])
    state.save_points(point)
    json_data = {"data": {"type": "Point", "coordinates": [["non-float", 1]]}}
    response = client.patch(f'/points/{point["id"]}', json=json_data)
    msg, err_type = "value is not a valid float", "type_error.float"
    assert_validation_err(response, ValidationError(["body", "data", "coordinates", 0, 0], msg, err_type))
    assert state.get_geometry_object(point["id"]) == point


def test_update_point__outside_lower_coord_bounds(state: TestState):
    point = state.create_point([1.0, 1.0])
    state.save_points(point)
    new_point = state.create_point([-180.1, -90.1], id=point["id"])
    response = client.patch(f'/points/{point["id"]}', json={"data": new_point["data"]})
    err_msg_1 = "x value needs to be between -180 and 180 (inclusive)."
    err_1 = ValidationError(["body", "data", "coordinates", 0, 0], err_msg_1, "value_error")
    err_msg_2 = "y value needs to be between -90 and 90 (inclusive)."
    err_2 = ValidationError(["body", "data", "coordinates", 0, 1], err_msg_2, "value_error")
    assert_validation_err(response, [err_1, err_2])
    assert state.get_geometry_object(point["id"]) == point


def test_update_point__outside_upper_coord_bounds(state: TestState):
    point = state.create_point([1.0, 1.0])
    state.save_points(point)
    new_point = state.create_point([180.1, 90.1], id=point["id"])
    response = client.patch(f'/points/{point["id"]}', json={"data": new_point["data"]})
    err_msg_1 = "x value needs to be between -180 and 180 (inclusive)."
    err_1 = ValidationError(["body", "data", "coordinates", 0, 0], err_msg_1, "value_error")
    err_msg_2 = "y value needs to be between -90 and 90 (inclusive)."
    err_2 = ValidationError(["body", "data", "coordinates", 0, 1], err_msg_2, "value_error")
    assert_validation_err(response, [err_1, err_2])
    assert state.get_geometry_object(point["id"]) == point
