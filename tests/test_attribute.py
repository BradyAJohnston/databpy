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
    with pytest.raises(AttributeError):
        db.named_attribute(obj, "test_attr")


def test_named_attribute_nonexistent():
    obj = db.create_object(np.array([[0, 0, 0]]), name="TestObject")

    with pytest.raises(AttributeError):
        db.named_attribute(obj, "nonexistent_attr")


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
