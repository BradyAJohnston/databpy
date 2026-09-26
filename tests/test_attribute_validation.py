"""Tests for input validation and lossless casting when storing attributes."""

import bpy
import numpy as np
import pytest

import databpy as db
from databpy.attribute import AttributeTypes, guess_atype_from_array


@pytest.fixture
def cube():
    return bpy.data.objects["Cube"]


def test_uint8_values_are_not_wrapped(cube):
    data = np.array([0, 100, 200, 255, 1, 2, 3, 4], dtype=np.uint8)
    db.store_named_attribute(cube, data, "values")
    assert np.array_equal(db.named_attribute(cube, "values"), data)


@pytest.mark.parametrize("dtype", [np.uint16, np.uint32])
def test_unsigned_2d_uses_int32(dtype):
    assert (
        guess_atype_from_array(np.zeros((4, 2), dtype=dtype)) == AttributeTypes.INT32_2D
    )


def test_integer_overflow_raises(cube):
    with pytest.raises(db.AttributeMismatchError, match="can't be stored"):
        db.store_named_attribute(cube, np.full(8, 2**33, dtype=np.int64), "big")


def test_integer_in_range_is_stored(cube):
    data = np.arange(8, dtype=np.int64) * 1000
    db.store_named_attribute(cube, data, "ids")
    assert np.array_equal(db.named_attribute(cube, "ids"), data)


def test_explicit_narrow_type_overflow_raises(cube):
    with pytest.raises(db.AttributeMismatchError):
        db.store_named_attribute(cube, np.full(8, 200), "small", atype="INT8")


def test_nan_into_int_raises(cube):
    data = np.arange(8, dtype=float)
    data[0] = np.nan
    with pytest.raises(db.AttributeMismatchError):
        db.store_named_attribute(cube, data, "ints", atype="INT")


def test_complex_raises(cube):
    with pytest.raises(ValueError, match="Unable to infer"):
        db.store_named_attribute(cube, np.ones(8, dtype=complex), "c")
    with pytest.raises(db.AttributeMismatchError, match="Complex"):
        db.store_named_attribute(cube, np.ones(8, dtype=complex), "c", atype="FLOAT")


def test_attribute_from_array_checks_overflow(cube):
    db.store_named_attribute(cube, np.zeros(8, dtype=np.int8), "small")
    attribute = db.Attribute(cube.data.attributes["small"])
    with pytest.raises(db.AttributeMismatchError):
        attribute.from_array(np.full(8, 1000))


@pytest.mark.parametrize(
    "data",
    [
        np.array(1.0),
        np.zeros((8, 5)),
        np.zeros((8, 2), dtype=bool),
        np.zeros((8, 3), dtype="U1"),
    ],
)
def test_uninferable_shapes_raise_clearly(cube, data):
    with pytest.raises(ValueError):
        db.store_named_attribute(cube, data, "bad")


def test_array_like_input(cube):
    db.store_named_attribute(cube, list(range(8)), "from_list")
    assert np.array_equal(db.named_attribute(cube, "from_list"), np.arange(8))
    db.store_named_attribute(cube, [0.5] * 8, "from_list_typed", atype="FLOAT")
    assert np.allclose(db.named_attribute(cube, "from_list_typed"), 0.5)

    attribute = db.Attribute(cube.data.attributes["from_list"])
    attribute.from_array(list(range(8, 16)))
    assert np.array_equal(attribute.as_array(), np.arange(8, 16))


def test_existing_attribute_type_used_when_atype_omitted(cube):
    db.store_named_attribute(cube, np.arange(8, dtype=np.int32), "ids")
    db.store_named_attribute(cube, np.arange(8, dtype=float) * 2, "ids")
    attribute = cube.data.attributes["ids"]
    assert attribute.data_type == "INT"
    assert np.array_equal(db.named_attribute(cube, "ids"), np.arange(8) * 2)


def test_explicit_atype_mismatch_still_raises(cube):
    db.store_named_attribute(cube, np.arange(8, dtype=np.int32), "ids")
    with pytest.raises(db.NamedAttributeError, match="does not match"):
        db.store_named_attribute(cube, np.arange(8.0), "ids", atype="FLOAT")


def test_existing_domain_used_when_domain_omitted(cube):
    db.store_named_attribute(cube, np.arange(6), "face_ids", domain="FACE")
    db.store_named_attribute(cube, np.arange(6) + 10, "face_ids")
    assert cube.data.attributes["face_ids"].domain == "FACE"
    assert np.array_equal(db.named_attribute(cube, "face_ids"), np.arange(6) + 10)


def test_explicit_domain_mismatch_raises(cube):
    db.store_named_attribute(cube, np.arange(6), "face_ids", domain="FACE")
    with pytest.raises(db.NamedAttributeError, match="already exists on the `FACE`"):
        db.store_named_attribute(cube, np.arange(8), "face_ids", domain="POINT")


@pytest.mark.parametrize(
    "create",
    [
        lambda: db.create_object(np.zeros((0, 3))),
        lambda: db.create_pointcloud_object(np.zeros((0, 3))),
        lambda: db.create_curves_object(),
    ],
)
def test_store_on_empty_geometry(create):
    obj = create()
    db.store_named_attribute(obj, np.zeros(0), "empty")
    assert "empty" in db.list_attributes(obj)
