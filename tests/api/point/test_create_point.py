from tests.conftest import TestState, ValidationError, assert_response, assert_validation_err, client


def test_create_point(state: TestState):
    json_data = {"data": {"type": "Point", "coordinates": [[1, 1]]}}
    response = client.post("/points", json=json_data)
    assert_response(response, 200, {"id": 1, **json_data})
    assert state.get_geometry_object(1) == {"id": 1, **json_data}


def test_create_point__lower_coord_bounds(state: TestState):
    json_data = {"data": {"type": "Point", "coordinates": [[-180, -90]]}}
    response = client.post("/points", json=json_data)
    assert_response(response, 200, {"id": 1, **json_data})
    assert state.get_geometry_object(1) == {"id": 1, **json_data}


def test_create_point__upper_coord_bounds(state: TestState):
    json_data = {"data": {"type": "Point", "coordinates": [[180, 90]]}}
    response = client.post("/points", json=json_data)
    assert_response(response, 200, {"id": 1, **json_data})
    assert state.get_geometry_object(1) == {"id": 1, **json_data}


def test_create_point__duplicate(state: TestState):
    json_data = {"data": {"type": "Point", "coordinates": [[1, 1]]}}
    response = client.post("/points", json=json_data)
    assert_response(response, 200, {"id": 1, **json_data})
    assert state.get_geometry_object(1) == {"id": 1, **json_data}
    response = client.post("/points", json=json_data)
    assert_response(response, 200, {"id": 2, **json_data})
    assert state.get_geometry_object(2) == {"id": 2, **json_data}


def test_create_point__invalid_type():
    json_data = {"data": {"type": "Contour", "coordinates": [[1, 1]]}}
    response = client.post("/points", json=json_data)
    error = ValidationError(
        ["body", "data", "type"],
        "unexpected value; permitted: 'Point'",
        "value_error.const",
        {"given": "Contour", "permitted": ["Point"]},
    )
    assert_validation_err(response, error)


def test_create_point__extra_fields():
    msg, err_type = "extra fields not permitted", "value_error.extra"

    json_data = {"extra": "field", "data": {"type": "Point", "coordinates": [[1, 1]]}}
    resp = client.post("/points", json=json_data)
    assert_validation_err(resp, ValidationError(["body", "extra"], msg, err_type))

    json_data = {"data": {"extra": "field", "type": "Point", "coordinates": [[1, 1]]}}
    resp = client.post("/points", json=json_data)
    assert_validation_err(resp, ValidationError(["body", "data", "extra"], msg, err_type))

    json_data = {"data": {"type": "Point", "coordinates": [[1, 1], "extra"]}}
    resp = client.post("/points", json=json_data)
    msg, err_type = "ensure this value has at most 1 items", "value_error.list.max_items"
    ctx = {"limit_value": 1}
    assert_validation_err(resp, ValidationError(["body", "data", "coordinates"], msg, err_type, ctx=ctx))


def test_create_point__not_2d_coord():
    json_data = {"data": {"type": "Point", "coordinates": [[1, 1, 1]]}}
    response = client.post("/points", json=json_data)
    msg, err_type = "wrong tuple length 3, expected 2", "value_error.tuple.length"
    ctx = {"actual_length": 3, "expected_length": 2}
    assert_validation_err(response, ValidationError(["body", "data", "coordinates", 0], msg, err_type, ctx=ctx))


def test_create_point__too_few_coords():
    json_data = {"data": {"type": "Point", "coordinates": []}}
    response = client.post("/points", json=json_data)
    msg, err_type = "ensure this value has at least 1 items", "value_error.list.min_items"
    ctx = {"limit_value": 1}
    assert_validation_err(response, ValidationError(["body", "data", "coordinates"], msg, err_type, ctx=ctx))


def test_create_point__too_many_coords():
    json_data = {"data": {"type": "Point", "coordinates": [[1, 1], [1, 1]]}}
    response = client.post("/points", json=json_data)
    msg, err_type = "ensure this value has at most 1 items", "value_error.list.max_items"
    ctx = {"limit_value": 1}
    assert_validation_err(response, ValidationError(["body", "data", "coordinates"], msg, err_type, ctx=ctx))


def test_create_point__single_set_coords():
    json_data = {"data": {"type": "Point", "coordinates": [1, 1]}}
    response = client.post("/points", json=json_data)
    msg, err_type = "ensure this value has at most 1 items", "value_error.list.max_items"
    ctx = {"limit_value": 1}
    assert_validation_err(response, ValidationError(["body", "data", "coordinates"], msg, err_type, ctx=ctx))


def test_create_point__invalid_coords():
    json_data = {"data": {"type": "Point", "coordinates": [["non-float", 1]]}}
    response = client.post("/points", json=json_data)
    msg, err_type = "value is not a valid float", "type_error.float"
    assert_validation_err(response, ValidationError(["body", "data", "coordinates", 0, 0], msg, err_type))


def test_create_point__outside_lower_coord_bounds():
    json_data = {"data": {"type": "Point", "coordinates": [[-180.1, -90.1]]}}
    response = client.post("/points", json=json_data)
    err_msg_1 = "x value needs to be between -180 and 180 (inclusive)."
    err_1 = ValidationError(["body", "data", "coordinates", 0, 0], err_msg_1, "value_error")
    err_msg_2 = "y value needs to be between -90 and 90 (inclusive)."
    err_2 = ValidationError(["body", "data", "coordinates", 0, 1], err_msg_2, "value_error")
    assert_validation_err(response, [err_1, err_2])


def test_create_point__outside_upper_coord_bounds():
    json_data = {"data": {"type": "Point", "coordinates": [[180.1, 90.1]]}}
    response = client.post("/points", json=json_data)
    err_msg_1 = "x value needs to be between -180 and 180 (inclusive)."
    err_1 = ValidationError(["body", "data", "coordinates", 0, 0], err_msg_1, "value_error")
    err_msg_2 = "y value needs to be between -90 and 90 (inclusive)."
    err_2 = ValidationError(["body", "data", "coordinates", 0, 1], err_msg_2, "value_error")
    assert_validation_err(response, [err_1, err_2])
