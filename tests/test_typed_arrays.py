from typing import assert_type

import bpy
import numpy as np
import pytest

import databpy as db


@pytest.fixture
def bob():
    bpy.ops.wm.read_factory_settings()
    return db.BlenderObject(bpy.data.objects["Cube"])


def test_wrap_casts_without_copying_matching_dtype():
    data = np.zeros((4, 3), dtype=np.float32)
    v = db.vec3(data)
    assert_type(v, db.vec3)
    assert isinstance(v, db.vec3)
    assert isinstance(v, db.AttributeArray)
    assert np.shares_memory(v, data)
    assert v._link is None

    v64 = db.vec3(np.zeros((4, 3)))
    assert v64.dtype == np.float32


@pytest.mark.parametrize(
    "cls, data",
    [
        (db.vec3, np.zeros(4)),
        (db.vec3, np.zeros((4, 4))),
        (db.float32, np.zeros((4, 1))),
        (db.mat4, np.zeros((4, 16))),
    ],
)
def test_wrap_wrong_shape_raises(cls, data):
    with pytest.raises(ValueError, match=cls.__name__):
        cls(data)


def test_wrap_out_of_range_raises():
    with pytest.raises(db.AttributeMismatchError):
        db.int8(np.array([1000]))


def test_wrap_linked_array_is_unlinked(bob: db.BlenderObject):
    v = db.vec3(bob.position)
    assert v._link is None
    v[0] = 10  # doesn't write to Blender
    assert not np.allclose(bob.position[0], 10)


def test_store_uses_declared_type(bob: db.BlenderObject):
    bob.point["c"] = db.color(np.ones((8, 4)))
    bob.point["q"] = db.quat(np.ones((8, 4)))
    bob.corner["uv"] = db.vec2(np.zeros((24, 2)))
    assert db.Attribute(bob.attributes["c"]).atype == db.AttributeTypes.FLOAT_COLOR
    assert db.Attribute(bob.attributes["q"]).atype == db.AttributeTypes.QUATERNION
    uv = db.Attribute(bob.attributes["uv"])
    assert uv.atype == db.AttributeTypes.FLOAT2
    assert uv.domain == db.AttributeDomains.CORNER


def test_store_mismatched_type_raises(bob: db.BlenderObject):
    bob.point["c"] = db.color(np.ones((8, 4)))
    with pytest.raises(db.NamedAttributeError):
        bob.point["c"] = db.quat(np.ones((8, 4)))
    with pytest.raises(db.NamedAttributeError):
        bob["c"] = db.quat(np.ones((8, 4)))
    with pytest.raises(db.NamedAttributeError):
        db.store_named_attribute(
            bob.object, db.quat(np.ones((8, 4))), "new", atype="FLOAT_COLOR"
        )


def test_read_returns_typed_subclass(bob: db.BlenderObject):
    pos = bob["position"]
    assert_type(pos, db.AttributeArray)
    assert type(pos) is db.vec3
    assert type(bob.point["position"]) is db.vec3

    bob.face["id"] = db.int32(np.arange(6))
    assert type(bob.face["id"]) is db.int32


def test_typed_key_access(bob: db.BlenderObject):
    pos = bob.point["position", db.vec3]
    assert_type(pos, db.vec3)
    pos[:, 2] += 1  # still writes back
    np.testing.assert_allclose(bob.position[:, 2], pos[:, 2])

    assert_type(bob["position", db.vec3], db.vec3)
    with pytest.raises(db.NamedAttributeError, match="FLOAT_VECTOR"):
        bob.point["position", db.color]
    with pytest.raises(db.NamedAttributeError, match="FLOAT_VECTOR"):
        bob["position", db.quat]


def test_named_attribute_atype(bob: db.BlenderObject):
    pos = db.named_attribute(bob.object, "position", atype=db.vec3)
    assert_type(pos, db.vec3)
    assert type(pos) is db.vec3
    assert pos._link is None

    assert_type(bob.named_attribute("position", atype=db.vec3), db.vec3)
    assert_type(bob.named_attribute("position"), np.ndarray)
    with pytest.raises(db.NamedAttributeError):
        db.named_attribute(bob.object, "position", atype=db.float32)


def test_views_that_change_shape_drop_the_type(bob: db.BlenderObject):
    pos = bob["position", db.vec3]
    column = pos[:, 0]
    assert type(column) is db.AttributeArray
    assert type(pos[0]) is db.AttributeArray
    assert type(pos[:4]) is db.vec3

    # the column is still synced
    column[:] = 5
    np.testing.assert_allclose(bob.position[:, 0], 5)

    # and is stored by its values, not as a vec3
    bob["x"] = column
    assert db.Attribute(bob.attributes["x"]).atype == db.AttributeTypes.FLOAT


def test_derived_arrays_are_plain(bob: db.BlenderObject):
    pos = bob["position", db.vec3]
    assert type(pos * 2) is np.ndarray
    assert type(pos + pos) is np.ndarray


def test_mat4_roundtrip(bob: db.BlenderObject):
    m = np.tile(np.eye(4, dtype=np.float32), (8, 1, 1))
    m[:, 0, 3] = np.arange(8)
    bob.point["m"] = db.mat4(m)
    out = bob.point["m", db.mat4]
    np.testing.assert_allclose(out, m)


def test_string_and_boolean(bob: db.BlenderObject):
    bob.point["b"] = db.boolean(np.arange(8) % 2 == 0)
    assert type(bob.point["b"]) is db.boolean
    with pytest.warns(UserWarning):
        bob.point["s"] = db.string(np.array(list("abcdefgh")))
