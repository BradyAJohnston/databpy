"""Tests that AttributeArray writes only the changed values into the attribute."""

import gc
import weakref
from types import SimpleNamespace
from typing import Any, cast

import numpy as np
import pytest

import databpy as db
import databpy.array
from databpy.attribute import HAS_FLOAT4, AttributeTypes, _attribute_memory


@pytest.fixture
def no_full_writes(monkeypatch):
    """Fail if an AttributeArray falls back to writing the entire attribute."""

    def fail(*args, **kwargs):
        raise AssertionError("the entire attribute was written with foreach_set")

    monkeypatch.setattr(databpy.array, "store_named_attribute", fail)


@pytest.fixture
def bob():
    return db.create_bob(np.random.rand(20, 3).astype(np.float32), name="TestObject")


WRITES = {
    "element": lambda a: a.__setitem__(0, [1, 2, 3]),
    "slice": lambda a: a.__setitem__(slice(2, 5), 7),
    "column": lambda a: a.__setitem__((slice(None, 10), 2), 10),
    "negative step": lambda a: a.__setitem__(slice(None, None, -3), -1),
    "mask": lambda a: a.__setitem__(a[:, 0] > 0.5, 0),
    "fancy": lambda a: a.__setitem__([1, 3, 3, 8], [4, 5, 6]),
    "view in-place": lambda a: a[:, 1].__iadd__(1),
    "reversed view": lambda a: a[::-1][0].__setitem__(slice(None), 9),
    "fill": lambda a: a.fill(3),
    "sort": lambda a: a.sort(axis=0),
    "putmask": lambda a: np.putmask(a, a > 0.5, 0.25),
    "empty slice": lambda a: a.__setitem__(slice(5, 5), 1),
    "empty view at end": lambda a: a[20:].__iadd__(1),
}


@pytest.mark.parametrize("write", WRITES.values(), ids=WRITES.keys())
def test_writes_directly(bob, no_full_writes, write):
    pos = bob.position
    write(pos)
    np.testing.assert_array_equal(bob.named_attribute("position"), pos)


def test_only_changed_values_are_written(bob):
    pos = bob.position
    # change the attribute after it was read, then write a single other value
    changed = bob.named_attribute("position")
    changed[5] = [100, 100, 100]
    bob.store_named_attribute(changed, "position")
    pos[0] = [1, 2, 3]

    result = bob.named_attribute("position")
    np.testing.assert_array_equal(result[0], [1, 2, 3])
    np.testing.assert_array_equal(result[5], [100, 100, 100])


DIRECT_TYPES = [
    t
    for t in AttributeTypes
    if t is not AttributeTypes.STRING and (HAS_FLOAT4 or t is not AttributeTypes.FLOAT4)
]


def _random_values(atype: AttributeTypes, n: int) -> np.ndarray:
    rng = np.random.default_rng(0)
    info = atype.value
    shape = (n,) if info.dimensions == (1,) else (n, *info.dimensions)
    if info.dtype == np.bool_:
        return rng.random(shape) > 0.5
    if np.issubdtype(info.dtype, np.integer):
        return rng.integers(0, 100, shape).astype(info.dtype)
    return rng.random(shape).astype(info.dtype)


@pytest.mark.parametrize("geometry", ["mesh", "pointcloud"])
@pytest.mark.parametrize("atype", DIRECT_TYPES, ids=lambda t: t.name)
def test_attribute_types(geometry, atype, no_full_writes):
    n = 20
    positions = np.random.rand(n, 3)
    if geometry == "mesh":
        obj = db.create_mesh_object(positions, name="TestObject")
    else:
        obj = db.create_pointcloud_object(positions, name="TestObject")
    bob = db.BlenderObject(obj)
    db.store_named_attribute(obj, _random_values(atype, n), "test", atype=atype)

    arr = bob["test"]
    new = _random_values(atype, n)[::-1]
    arr[3:7] = new[3:7]
    arr[-1] = new[-1]

    expected = np.asarray(bob.named_attribute("test"))
    np.testing.assert_array_equal(expected[3:7], new[3:7])
    np.testing.assert_array_equal(expected[-1], new[-1])
    np.testing.assert_array_equal(expected, arr)


def test_evaluated_geometry_updates(bob, no_full_writes):
    pos = bob.position
    pos[0] = [5, 6, 7]
    evaluated = db.named_attribute(bob.object, "position", evaluate=True)
    np.testing.assert_array_equal(evaluated[0], [5, 6, 7])


@pytest.mark.filterwarnings("ignore:String attributes")
def test_strings_write_entire_attribute(bob, monkeypatch):
    bob.store_named_attribute(np.array(["a"] * 20), "names", atype="STRING")
    calls = []
    original = databpy.array.store_named_attribute

    def counting(*args, **kwargs):
        calls.append(1)
        return original(*args, **kwargs)

    monkeypatch.setattr(databpy.array, "store_named_attribute", counting)
    names = bob["names"]
    names[0] = "b"
    assert len(calls) == 1
    assert bob.named_attribute("names")[0] == "b"


def test_empty_attribute(bob):
    # the mesh has no faces, so there are no values to write directly
    bob.store_named_attribute(np.zeros(0), "face_values", domain="FACE")
    values = bob["face_values"]
    values += 1
    assert bob.named_attribute("face_values").shape == (0,)


def test_removed_attribute_is_created_again(bob):
    bob.store_named_attribute(np.arange(20), "ids")
    ids = bob["ids"]
    db.remove_named_attribute(bob.object, "ids")
    ids[0] = 99
    np.testing.assert_array_equal(bob.named_attribute("ids"), [99, *range(1, 20)])


class _Value:
    def __init__(self, pointer: int):
        self.pointer = pointer

    def as_pointer(self) -> int:
        return self.pointer


@pytest.mark.parametrize(
    "pointers",
    [[1000, 1012, 2000], [0, 12, 24]],
    ids=["not contiguous", "null pointer"],
)
def test_attribute_memory_requires_contiguous_values(pointers):
    # Blender's values are always contiguous, but nothing is written directly into
    # memory that isn't laid out as expected
    attribute = SimpleNamespace(
        storage_type="ARRAY", data=[_Value(p) for p in pointers]
    )
    assert _attribute_memory(cast(Any, attribute), AttributeTypes.FLOAT_VECTOR) is None


def test_resized_attribute_is_not_written_directly(bob):
    pos = bob.position
    bob.data.vertices.add(5)
    # the attribute no longer matches the array, so writing falls back to
    # `store_named_attribute`, which reports the size mismatch
    with pytest.raises(db.NamedAttributeError, match="does not match"):
        pos[0] = [1, 2, 3]


def test_arrays_are_freed_without_garbage_collection(bob):
    gc.disable()
    try:
        pos = bob.position
        view = pos[:, 2]
        ref, view_ref = weakref.ref(pos), weakref.ref(view)
        del pos, view
        assert ref() is None
        assert view_ref() is None
    finally:
        gc.enable()
