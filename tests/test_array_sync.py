"""Tests that every in-place modification of an AttributeArray syncs to Blender."""

import bpy
import numpy as np
import pytest

import databpy as db
import databpy.array


@pytest.fixture
def bob():
    bob = db.create_bob(np.random.rand(10, 3))
    bob.store_named_attribute(np.arange(10, dtype=np.int32), "ids")
    return bob


def _assert_synced(bob, name, arr):
    assert np.array_equal(bob.named_attribute(name), np.asarray(arr))


@pytest.mark.parametrize(
    "operation",
    [
        lambda a: a.__iadd__(1),
        lambda a: a.__isub__(1),
        lambda a: a.__imul__(2),
        lambda a: a.__ipow__(2),
        lambda a: a.__ifloordiv__(2),
        lambda a: a.__imod__(3),
        lambda a: a.__ior__(1),
        lambda a: a.__iand__(6),
        lambda a: a.__ixor__(5),
        lambda a: a.__ilshift__(1),
        lambda a: a.__irshift__(1),
        lambda a: np.add(a, 5, out=a),
        lambda a: np.clip(a, 2, 5, out=a),
        lambda a: np.add.at(a, [0, 0, 1], 1),
        lambda a: a.fill(7),
        lambda a: a.put([0, 1], [50, 60]),
        lambda a: a.__setitem__(slice(None), a[::-1].copy()) or a.sort(),
        lambda a: a.partition(3),
        lambda a: np.copyto(a, np.full(10, 3)),
        lambda a: np.place(a, a > 4, [0]),
        lambda a: np.putmask(a, a > 4, 1),
    ],
)
def test_inplace_operations_sync(bob, operation):
    ids = bob["ids"]
    operation(ids)
    _assert_synced(bob, "ids", ids)


def test_float_inplace_operations_sync(bob):
    pos = bob.position
    pos /= 2
    _assert_synced(bob, "position", pos)
    pos[:, 2] **= 2
    _assert_synced(bob, "position", pos)
    np.fill_diagonal(pos, 0)
    _assert_synced(bob, "position", pos)


def test_inplace_keeps_attribute_array_type(bob):
    pos = bob.position
    pos += 1
    assert isinstance(pos, db.AttributeArray)


def test_new_arrays_do_not_sync(bob):
    before = bob.named_attribute("position")
    pos = bob.position
    result = pos + 1
    assert type(result) is np.ndarray
    copy = pos.copy()
    copy += 1
    masked = pos[pos[:, 0] > 0.5]
    masked += 1
    assert np.array_equal(bob.named_attribute("position"), before)


def test_view_augmented_assignment_syncs_once(bob, monkeypatch):
    calls = []
    original = databpy.array.store_named_attribute

    def counting(*args, **kwargs):
        calls.append(1)
        return original(*args, **kwargs)

    monkeypatch.setattr(databpy.array, "store_named_attribute", counting)
    pos = bob.position
    pos[:, 2] += 1
    assert len(calls) == 1
    _assert_synced(bob, "position", pos)

    calls.clear()
    pos[pos[:, 0] > 0.5] += 1
    assert len(calls) == 1
    _assert_synced(bob, "position", pos)


def test_survives_object_rename_and_new_attributes(bob):
    pos = bob.position
    bob.object.name = "Renamed"
    for i in range(20):
        bob.store_named_attribute(np.random.rand(10), f"attr_{i}")
    pos[0] = [9, 9, 9]
    assert np.allclose(bob.named_attribute("position")[0], 9)


def test_removed_object_raises(bob):
    pos = bob.position
    bpy.data.objects.remove(bob.object)
    with pytest.raises(db.LinkedObjectError, match="has been removed"):
        pos[0] = [1, 2, 3]
    # printing a disconnected array still works
    assert "position" in repr(pos)


def test_file_load_raises(bob, tmp_path):
    pos = bob.position
    path = str(tmp_path / "sync.blend")
    bpy.ops.wm.save_as_mainfile(filepath=path)
    bpy.ops.wm.open_mainfile(filepath=path)
    with pytest.raises(db.LinkedObjectError, match="file was loaded"):
        pos[0] = [1, 2, 3]
