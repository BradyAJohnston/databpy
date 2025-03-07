import pytest
import numpy as np
import bpy
import databpy as db


def test_named_attribute_position():
    # Create test object with known vertices
    verts = np.array([[0, 0, 0], [1, 1, 1], [2, 2, 2]])
    obj = db.create_object(verts, name="TestObject")

    # Test retrieving position attribute
    result = db.named_attribute(obj, "position")
    np.testing.assert_array_equal(result, verts)


def test_named_attribute_custom():
    # Create test object
    verts = np.array([[0, 0, 0], [1, 1, 1]])
    obj = db.create_object(verts, name="TestObject")

    # Store custom attribute
    test_data = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    db.store_named_attribute(obj, test_data, "test_attr")

    # Test retrieving custom attribute
    result = db.named_attribute(obj, "test_attr")
    np.testing.assert_array_equal(result, test_data)

    db.remove_named_attribute(obj, "test_attr")
    with pytest.raises(db.attribute.NamedAttributeError):
        db.named_attribute(obj, "test_attr")


def test_named_attribute_nonexistent():
    obj = db.create_object(np.array([[0, 0, 0]]), name="TestObject")

    with pytest.raises(AttributeError):
        db.named_attribute(obj, "nonexistent_attr")


def test_attribute_mismatch():
    # Create test object
    verts = np.array([[0, 0, 0], [1, 1, 1]])
    obj = db.create_object(verts, name="TestObject")
    new_data = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    db.store_named_attribute(obj, new_data, "test_attr")

    test_data = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 1.0, 0.0]])

    with pytest.raises(db.attribute.NamedAttributeError):
        db.store_named_attribute(obj, test_data, "test_attr")

    with pytest.raises(db.attribute.NamedAttributeError):
        db.store_named_attribute(obj, np.repeat(1, 3), "test_attr")


def test_attribute_overwrite():
    verts = np.array([[0, 0, 0], [1, 1, 1]])
    obj = db.create_object(verts, name="TestObject")
    new_data = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    db.store_named_attribute(obj, new_data, "test_attr")
    # with overwrite = False, the attribute should not be overwritten and a new one will
    # be created with a new name instead
    new_values = np.repeat(1, 2)
    att = db.store_named_attribute(obj, new_values, "test_attr", overwrite=False)

    assert new_values.shape != db.named_attribute(obj, "test_attr").shape
    assert np.allclose(new_values, db.named_attribute(obj, att.name))

    assert db.named_attribute(obj, "test_attr").shape == (2, 3)
    with pytest.raises(db.attribute.NamedAttributeError):
        db.store_named_attribute(obj, new_values, "test_attr")

    db.remove_named_attribute(obj, "test_attr")
    with pytest.raises(db.attribute.NamedAttributeError):
        db.named_attribute(obj, "test_attr")
    db.store_named_attribute(obj, new_values, "test_attr")
    assert np.allclose(db.named_attribute(obj, "test_attr"), new_values)
    assert db.named_attribute(obj, "test_attr").shape == (2,)


def test_named_attribute_evaluate():
    # Create test object with modifier
    obj = bpy.data.objects["Cube"]
    pos = db.named_attribute(obj, "position")

    # Add a simple modifier (e.g., subdivision surface)
    mod = obj.modifiers.new(name="Subsurf", type="SUBSURF")
    mod.levels = 1

    # Test with evaluate=True
    result = db.named_attribute(obj, "position", evaluate=True)
    assert len(result) > len(pos)  # Should have more vertices after subdivision


def test_obj_type_error():
    with pytest.raises(TypeError):
        db.named_attribute(123, "position")

    with pytest.raises(TypeError):
        db.named_attribute(bpy.data.objects["Camera"], "position")


def test_check_obj():
    db.attribute._check_obj_attributes(bpy.data.objects["Cube"])
    assert pytest.raises(
        TypeError,
        db.attribute._check_obj_attributes,
        bpy.data.objects["Camera"],
    )
    assert pytest.raises(
        TypeError,
        db.attribute._check_obj_attributes,
        bpy.data.objects["Light"],
    )
    assert pytest.raises(
        TypeError,
        db.attribute._check_is_mesh,
        bpy.data.objects["Light"],
    )
    assert pytest.raises(
        TypeError,
        db.attribute._check_is_mesh,
        bpy.data.objects["Camera"],
    )


def test_guess_attribute_type():
    # Create test object
    verts = np.array([[0, 0, 0], [1, 1, 1]])
    assert pytest.raises(
        ValueError,
        db.attribute.guess_atype_from_array,
        ["A", "B", "C"],
    )


def test_guess_atype():
    assert (
        db.attribute.AttributeTypes.FLOAT_COLOR
        == db.attribute.guess_atype_from_array(np.zeros((10, 4)))
    )
    assert (
        db.attribute.AttributeTypes.FLOAT_VECTOR
        == db.attribute.guess_atype_from_array(np.zeros((10, 3)))
    )
    assert db.attribute.AttributeTypes.BOOLEAN == db.attribute.guess_atype_from_array(
        np.zeros(10, dtype=bool)
    )


def test_raise_error():
    with pytest.raises(db.attribute.NamedAttributeError):
        db.store_named_attribute(bpy.data.objects["Cube"], np.zeros((10, 3)), "test")

    with pytest.raises(db.attribute.NamedAttributeError):
        db.remove_named_attribute(bpy.data.objects["Cube"], "testing")
