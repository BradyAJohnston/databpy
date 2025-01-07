import databpy as db
import bpy
import numpy as np
import pytest

np.random.seed(11)


def test_get_position(snapshot):
    bpy.ops.wm.read_factory_settings()

    att = db.named_attribute(bpy.data.objects["Cube"], "position")
    assert snapshot == att


def test_set_position(snapshot):
    bpy.ops.wm.read_factory_settings()
    obj = bpy.data.objects["Cube"]
    pos_a = db.named_attribute(obj, "position")
    db.store_named_attribute(
        obj, np.random.randn(len(obj.data.vertices), 3), "position"
    )
    pos_b = db.named_attribute(obj, "position")
    assert not np.allclose(pos_a, pos_b)
    assert snapshot == pos_a
    assert snapshot == pos_b


def test_bob(snapshot):
    bpy.ops.wm.read_factory_settings()
    bob = db.BlenderObject(bpy.data.objects["Cube"])

    pos_a = bob.named_attribute("position")
    bob.store_named_attribute(np.random.randn(len(bob), 3), "position")
    pos_b = bob.named_attribute("position")
    assert not np.allclose(pos_a, pos_b)
    assert snapshot == pos_a
    assert snapshot == pos_b


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
    bob = db.BlenderObject(bpy.data.objects["Cube"])
