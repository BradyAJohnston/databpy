import bpy
import numpy as np
import pytest

import databpy as db


@pytest.fixture
def bob():
    bpy.ops.wm.read_factory_settings()
    return db.BlenderObject(bpy.data.objects["Cube"])


def test_len(bob):
    assert len(bob.point) == 8
    assert len(bob.edge) == 12
    assert len(bob.face) == 6
    assert len(bob.corner) == 24
    assert len(bob.curve) == 0


def test_set_new_attribute_on_domain(bob):
    bob.face["area"] = np.arange(6, dtype=float)
    att = db.Attribute(bob.attributes["area"])
    assert att.domain == db.AttributeDomains.FACE
    assert att.atype == db.AttributeTypes.FLOAT
    np.testing.assert_allclose(bob.face["area"], np.arange(6))
    assert "area" in bob.face
    assert "area" not in bob.point
    assert "area" in bob.face.list_attributes()


def test_overwrite_same_domain(bob):
    bob.face["area"] = np.zeros(6)
    bob.face["area"] = np.ones(6)
    np.testing.assert_allclose(bob.face["area"], 1)


def test_get_mismatched_domain_raises(bob):
    bob.face["area"] = np.zeros(6)
    with pytest.raises(db.NamedAttributeError, match="FACE"):
        bob.point["area"]


def test_set_mismatched_domain_raises(bob):
    bob.face["area"] = np.zeros(6)
    with pytest.raises(db.NamedAttributeError, match="FACE"):
        bob.edge["area"] = np.zeros(12)


def test_missing_attribute_raises(bob):
    with pytest.raises(db.AttributeNotFoundError):
        bob.face["missing"]


def test_wrong_size_raises(bob):
    with pytest.raises(db.NamedAttributeError):
        bob.face["area"] = np.zeros(8)


def test_unsupported_domain_raises():
    bob = db.BlenderObject(db.create_pointcloud_object(np.zeros((5, 3))))
    assert len(bob.face) == 0
    with pytest.raises(db.NamedAttributeError):
        bob.face["x"] = np.zeros(0)
