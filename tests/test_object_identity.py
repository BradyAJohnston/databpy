"""Tests for how BlenderObjectBase tracks its object within and across sessions."""

import pickle

import bpy
import numpy as np
import pytest

import databpy as db
from databpy.addon import UUID_KEY


def _duplicate(obj: bpy.types.Object) -> bpy.types.Object:
    dup = obj.copy()
    bpy.context.scene.collection.objects.link(dup)
    return dup


def test_uuid_stored_as_custom_property():
    bob = db.BlenderObject(bpy.data.objects["Cube"])
    assert bob.object[UUID_KEY] == bob.uuid
    # kept in sync with the deprecated registered property during the window
    assert bob.object.uuid == bob.uuid


def test_survives_rename_and_geometry_changes():
    bob = db.BlenderObject(bpy.data.objects["Cube"])
    bpy.data.objects["Cube"].name = "Renamed"
    bob.data.vertices.add(4)
    for i in range(20):
        bob.data.attributes.new(f"attr_{i}", "FLOAT", "POINT")

    assert bob.name == "Renamed"
    assert len(bob) == 12
    assert "attr_19" in bob.list_attributes()


def test_duplicate_is_not_mistaken_for_original():
    bob = db.BlenderObject(bpy.data.objects["Cube"])
    dup = _duplicate(bob.object)
    # the copy shares the persistent uuid but has its own session_uid
    assert dup[UUID_KEY] == bob.uuid

    bob.object.name = "Original"
    dup.name = "Cube"
    assert bob.name == "Original"


def test_removed_object_raises_instead_of_retargeting():
    bob = db.BlenderObject(bpy.data.objects["Cube"])
    _duplicate(bob.object)
    bpy.data.objects.remove(bob.object)

    with pytest.raises(db.LinkedObjectError, match="has been removed"):
        bob.object


def test_reconnects_after_file_reload(tmp_path):
    bob = db.BlenderObject(bpy.data.objects["Cube"])
    bob.store_named_attribute(np.arange(8), "ids")
    old_session_uid = bob.object.session_uid

    path = str(tmp_path / "identity.blend")
    bpy.ops.wm.save_as_mainfile(filepath=path)
    bpy.ops.wm.open_mainfile(filepath=path)

    assert bob.object.session_uid != old_session_uid
    assert bob.name == "Cube"
    assert np.array_equal(bob.named_attribute("ids"), np.arange(8))


def test_reconnects_after_file_reload_and_rename(tmp_path):
    bob = db.BlenderObject(bpy.data.objects["Cube"])
    path = str(tmp_path / "identity.blend")
    bpy.ops.wm.save_as_mainfile(filepath=path)
    bpy.ops.wm.open_mainfile(filepath=path)
    bpy.data.objects["Cube"].name = "Renamed"

    assert bob.name == "Renamed"


def test_reload_prefers_original_name_over_duplicate(tmp_path):
    bob = db.BlenderObject(bpy.data.objects["Cube"])
    dup = _duplicate(bob.object)
    dup.name = "Copy"
    path = str(tmp_path / "identity.blend")
    bpy.ops.wm.save_as_mainfile(filepath=path)
    bpy.ops.wm.open_mainfile(filepath=path)

    assert bob.name == "Cube"


def test_unpickled_wrapper_reconnects_by_uuid():
    # simulates a wrapper restored in a new session, where cached session_uid
    # values must not be trusted
    bob = db.BlenderObject(bpy.data.objects["Cube"])
    restored = pickle.loads(pickle.dumps(bob))
    restored._session_token = "previous-session"
    restored._session_uid = -1

    assert restored.name == "Cube"


def test_migrates_legacy_uuid():
    obj = bpy.data.objects["Cube"]
    db.addon._ensure_legacy_property()
    obj.uuid = "legacy-uuid"
    assert UUID_KEY not in obj

    bob = db.BlenderObject(obj)
    assert bob.uuid == "legacy-uuid"
    assert obj[UUID_KEY] == "legacy-uuid"


def test_create_bob_with_uuid():
    bob = db.create_bob(np.zeros((3, 3)), uuid="given-uuid")
    assert bob.uuid == "given-uuid"
    assert bob.object[UUID_KEY] == "given-uuid"
    assert len(bob) == 3
