from typing import Any

import bpy
import numpy as np
import pytest

import databpy as db

np.random.seed(11)


def test_get_position():
    bpy.ops.wm.read_factory_settings()

    att = db.named_attribute(bpy.data.objects["Cube"], "position")
    # Verify basic properties of the position attribute
    assert att.shape == (8, 3)  # Default cube has 8 vertices
    assert att.dtype in (np.float32, np.float64)  # Should be float type
    # Verify it contains reasonable position data
    assert np.all(np.abs(att) <= 10.0)  # Positions should be reasonable values


def test_set_position():
    bpy.ops.wm.read_factory_settings()
    obj = bpy.data.objects["Cube"]
    pos_a = db.named_attribute(obj, "position")

    # Store new random positions
    new_positions = np.random.randn(len(db.mesh_data(obj).vertices), 3)
    db.store_named_attribute(obj, new_positions, "position")
    pos_b = db.named_attribute(obj, "position")

    # Verify positions changed
    assert not np.allclose(pos_a, pos_b)
    # Verify new positions match what we set
    assert np.allclose(pos_b, new_positions)
    # Verify shapes are correct
    assert pos_a.shape == (8, 3)
    assert pos_b.shape == (8, 3)


def test_bob():
    bpy.ops.wm.read_factory_settings()
    bob = db.BlenderObject(bpy.data.objects["Cube"])

    pos_a = bob.named_attribute("position")

    # Store new random positions
    new_positions = np.random.randn(len(bob), 3)
    bob.store_named_attribute(new_positions, "position")
    pos_b = bob.named_attribute("position")

    # Verify positions changed
    assert not np.allclose(pos_a, pos_b)
    # Verify new positions match what we set
    assert np.allclose(pos_b, new_positions)
    # Verify shapes and basic properties
    assert pos_a.shape == (8, 3)
    assert pos_b.shape == (8, 3)
    assert len(bob) == 8  # Default cube has 8 vertices


# test that we aren't overwriting an existing UUID on an object, when wrapping it with
# with BlenderObject
def test_bob_mismatch_uuid():
    bob = db.BlenderObject(bpy.data.objects["Cube"])
    obj = bob.object
    old_uuid = db.object.get_uuid(obj)
    bob = db.BlenderObject(obj)
    assert old_uuid == bob.uuid


def test_register():
    db.unregister()
    db.BlenderObject(bpy.data.objects["Cube"])


def test_set_uuid_registers_property():
    # after unregistering, setting a uuid re-registers the dynamic property
    obj = bpy.data.objects["Cube"]
    db.unregister()
    db.object.set_uuid(obj, "test-uuid-register")
    assert db.object.get_uuid(obj) == "test-uuid-register"


def test_object_setter_requires_object():
    bob = db.create_bob(np.zeros((3, 3)))
    not_an_object: Any = 123
    with pytest.raises(TypeError):
        bob.object = not_an_object


def test_create_bob_with_uuid():
    bob = db.create_bob(np.zeros((3, 3)), uuid="my-custom-uuid")
    assert bob.uuid == "my-custom-uuid"
    assert db.object.get_uuid(bob.object) == "my-custom-uuid"


def test_blender_object_from_name_keeps_uuid():
    # wrapping by name picks up the uuid already stored on the object
    bob = db.BlenderObject(bpy.data.objects["Cube"])
    bob_by_name = db.BlenderObject("Cube")
    assert bob_by_name.uuid == bob.uuid


def test_bob_remove_named_attribute():
    bob = db.create_bob(np.random.rand(4, 3))
    bob.store_named_attribute(np.arange(4), "to_remove")
    assert "to_remove" in bob.list_attributes()
    bob.remove_named_attribute("to_remove")
    assert "to_remove" not in bob.list_attributes()
