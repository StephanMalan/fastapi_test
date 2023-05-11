from tests.conftest import TestState, ValidationError, assert_response, assert_validation_err, client


def test_create_contour(state: TestState):
    json_data = {"data": {"type": "Contour", "coordinates": [[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]}}
    response = client.post("/contours", json=json_data)
    assert_response(response, 200, {"id": 1, **json_data})
    assert state.get_geometry_object(1) == {"id": 1, **json_data}


def test_create_contour__coord_bounds(state: TestState):
    coords = [[180, 90], [180, -90], [-180, -90], [-180, 90], [180, 90]]
    json_data = {"data": {"type": "Contour", "coordinates": coords}}
    response = client.post("/contours", json=json_data)
    assert_response(response, 200, {"id": 1, **json_data})
    assert state.get_geometry_object(1) == {"id": 1, **json_data}


def test_create_contour__duplicate(state: TestState):
    json_data = {"data": {"type": "Contour", "coordinates": [[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]}}
    response = client.post("/contours", json=json_data)
    assert_response(response, 200, {"id": 1, **json_data})
    assert state.get_geometry_object(1) == {"id": 1, **json_data}
    response = client.post("/contours", json=json_data)
    assert_response(response, 200, {"id": 2, **json_data})
    assert state.get_geometry_object(2) == {"id": 2, **json_data}


def test_create_contour__invalid_type():
    json_data = {"data": {"type": "Point", "coordinates": [[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]}}
    response = client.post("/contours", json=json_data)
    error = ValidationError(
        ["body", "data", "type"],
        "unexpected value; permitted: 'Contour'",
        "value_error.const",
        {"given": "Point", "permitted": ["Contour"]},
    )
    assert_validation_err(response, error)


def test_create_contour__extra_fields():
    msg, err_type = "extra fields not permitted", "value_error.extra"

    json_data = {"extra": "field", "data": {"type": "Contour", "coordinates": [[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]}}
    resp = client.post("/contours", json=json_data)
    assert_validation_err(resp, ValidationError(["body", "extra"], msg, err_type))

    json_data = {"data": {"extra": "field", "type": "Contour", "coordinates": [[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]}}
    resp = client.post("/contours", json=json_data)
    assert_validation_err(resp, ValidationError(["body", "data", "extra"], msg, err_type))

    json_data = {"data": {"type": "Contour", "coordinates": [[0, 0], [0, 1], [1, 1], [1, 0], [0, 0], "extra"]}}
    resp = client.post("/contours", json=json_data)
    msg, err_type = "value is not a valid tuple", "type_error.tuple"
    assert_validation_err(resp, ValidationError(["body", "data", "coordinates", 5], msg, err_type))


def test_create_contour__not_2d_coord():
    json_data = {"data": {"type": "Contour", "coordinates": [[0, 0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]}}
    response = client.post("/contours", json=json_data)
    msg, err_type = "wrong tuple length 3, expected 2", "value_error.tuple.length"
    ctx = {"actual_length": 3, "expected_length": 2}
    assert_validation_err(response, ValidationError(["body", "data", "coordinates", 0], msg, err_type, ctx=ctx))


def test_create_contour__too_few_coords():
    json_data = {"data": {"type": "Contour", "coordinates": [[0, 0], [1, 1], [0, 0]]}}
    response = client.post("/contours", json=json_data)
    msg, err_type = "ensure this value has at least 4 items", "value_error.list.min_items"
    ctx = {"limit_value": 4}
    assert_validation_err(response, ValidationError(["body", "data", "coordinates"], msg, err_type, ctx=ctx))


def test_create_contour__single_set_coords():
    json_data = {"data": {"type": "Contour", "coordinates": [1, 1]}}
    response = client.post("/contours", json=json_data)
    msg, err_type = "ensure this value has at least 4 items", "value_error.list.min_items"
    ctx = {"limit_value": 4}
    assert_validation_err(response, ValidationError(["body", "data", "coordinates"], msg, err_type, ctx=ctx))


def test_create_contour__invalid_coords():
    json_data = {"data": {"type": "Contour", "coordinates": [["invalid", 0], [0, 1], [1, 1], [1, 0], [0, 0]]}}
    response = client.post("/contours", json=json_data)
    msg, err_type = "value is not a valid float", "type_error.float"
    assert_validation_err(response, ValidationError(["body", "data", "coordinates", 0, 0], msg, err_type))


def test_create_contour__outside_coord_bounds():
    json_data = {"data": {"type": "Contour", "coordinates": [[0, 1], [180.1, 90.1], [1, 0], [-180.1, -90.1], [0, 1]]}}
    response = client.post("/contours", json=json_data)
    x_err_msg = "x value needs to be between -180 and 180 (inclusive)."
    y_err_msg = "y value needs to be between -90 and 90 (inclusive)."
    err_1 = ValidationError(["body", "data", "coordinates", 1, 0], x_err_msg, "value_error")
    err_2 = ValidationError(["body", "data", "coordinates", 1, 1], y_err_msg, "value_error")
    err_3 = ValidationError(["body", "data", "coordinates", 3, 0], x_err_msg, "value_error")
    err_4 = ValidationError(["body", "data", "coordinates", 3, 1], y_err_msg, "value_error")
    assert_validation_err(response, [err_1, err_2, err_3, err_4])


def test_create_contour__non_simple_polygon():
    json_data = {"data": {"type": "Contour", "coordinates": [[0, 0], [1, 1], [1, 0], [0, 1], [0, 0]]}}
    response = client.post("/contours", json=json_data)
    msg, err_type = "contour is not a simple polygon.", "value_error"
    assert_validation_err(response, ValidationError(["body", "data", "coordinates", 0], msg, err_type))


def test_create_contour__not_closed():
    json_data = {"data": {"type": "Contour", "coordinates": [[0, 0], [0, 1], [1, 1], [1, 0]]}}
    response = client.post("/contours", json=json_data)
    msg, err_type = "contour is not closed.", "value_error"
    assert_validation_err(response, ValidationError(["body", "data", "coordinates", 0], msg, err_type))
