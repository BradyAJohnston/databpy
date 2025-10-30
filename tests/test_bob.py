import databpy as db
import bpy
import numpy as np

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
    new_positions = np.random.randn(len(obj.data.vertices), 3)
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
    old_uuid = obj.uuid
    bob = db.BlenderObject(obj)
    assert old_uuid == bob.uuid


def test_register():
    db.unregister()
    db.BlenderObject(bpy.data.objects["Cube"])
