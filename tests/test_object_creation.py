"""Tests for creating objects and related helpers."""

import bpy
import numpy as np
import pytest

import databpy as db


def test_mixed_face_sizes():
    obj = db.create_object(np.random.rand(5, 3), faces=[[0, 1, 2], [1, 2, 3, 4]])
    assert [len(face.vertices) for face in db.mesh_data(obj).polygons] == [3, 4]


def test_face_array():
    obj = db.create_object(np.random.rand(4, 3), faces=np.array([[0, 1, 2, 3]]))
    assert len(db.mesh_data(obj).polygons) == 1


@pytest.mark.parametrize(
    "kwargs",
    [{"faces": [[0, 1, 7]]}, {"edges": [[0, -1]]}, {"faces": np.array([[0, 1, 3]])}],
)
def test_out_of_range_indices_raise(kwargs):
    with pytest.raises(ValueError, match="outside of the 3 vertices"):
        db.create_object(np.zeros((3, 3)), **kwargs)


def test_new_from_pydata_checks_indices():
    bob = db.create_bob(np.zeros((3, 3)))
    with pytest.raises(ValueError, match="outside"):
        bob.new_from_pydata(np.zeros((3, 3)), faces=[[0, 1, 5]])
    # the existing geometry is left intact
    assert len(bob) == 3


def _mesh_attributes(mesh, skip_empty: bool = False) -> dict[str, tuple[str, list]]:
    attributes = {
        a.name: (a.domain, db.Attribute(a).as_array().tolist()) for a in mesh.attributes
    }
    if skip_empty:
        return {k: v for k, v in attributes.items() if v[1]}
    return attributes


@pytest.mark.parametrize(
    "edges, faces",
    [
        (None, None),
        ([[0, 1], [3, 4]], None),
        (None, np.array([[0, 1, 2], [1, 2, 3]])),
        (None, [[0, 1, 2], [1, 2, 3, 4]]),
        ([[0, 4], [0, 1]], [(0, 1, 2), (1, 2, 3, 4)]),
    ],
)
def test_matches_from_pydata(edges, faces):
    vertices = np.random.rand(6, 3)
    expected = bpy.data.meshes.new("expected")
    expected.from_pydata(
        vertices, [] if edges is None else edges, [] if faces is None else faces
    )

    mesh = db.mesh_data(db.create_object(vertices, edges, faces))
    assert not mesh.validate()
    assert _mesh_attributes(mesh) == _mesh_attributes(expected)

    # clearing the existing geometry can leave behind empty attributes
    bob = db.create_bob(np.zeros((2, 3)), faces=[[0, 1, 0]])
    bob.new_from_pydata(vertices, edges, faces)
    assert _mesh_attributes(bob.data, skip_empty=True) == _mesh_attributes(
        expected, skip_empty=True
    )


def test_empty_mesh_matches_from_pydata():
    expected = bpy.data.meshes.new("expected")
    expected.from_pydata([], [], [])
    mesh = db.mesh_data(db.create_object())
    assert _mesh_attributes(mesh) == _mesh_attributes(expected)


@pytest.mark.parametrize(
    "kwargs, error",
    [
        ({"vertices": np.zeros((3, 2))}, ValueError),
        ({"vertices": np.zeros((3, 3)), "edges": [[0, 1, 2]]}, ValueError),
        ({"vertices": np.zeros((3, 3)), "faces": [[0.0, 1.0, 2.0]]}, TypeError),
    ],
)
def test_invalid_mesh_data_raises(kwargs, error):
    n_meshes = len(bpy.data.meshes)
    with pytest.raises(error):
        db.create_object(**kwargs)
    assert len(bpy.data.meshes) == n_meshes


def test_pointcloud_in_unlinked_collection():
    collection = bpy.data.collections.new("Unlinked")
    obj = db.create_pointcloud_object(np.random.rand(4, 3), collection=collection)
    assert obj.type == "POINTCLOUD"
    assert len(db.pointcloud_data(obj).points) == 4
    assert obj.users_collection[0] == collection


def test_pointcloud_positions_and_no_orphan_mesh():
    positions = np.random.rand(6, 3)
    n_meshes = len(bpy.data.meshes)
    obj = db.create_pointcloud_object(positions)
    assert len(bpy.data.meshes) == n_meshes
    assert np.allclose(db.named_attribute(obj, "position"), positions)


def test_empty_pointcloud():
    obj = db.create_pointcloud_object()
    assert obj.type == "POINTCLOUD"
    assert len(db.pointcloud_data(obj).points) == 0


@pytest.mark.parametrize(
    "kwargs", [{"positions": np.zeros((5, 3))}, {"curve_sizes": [2, 3]}]
)
def test_curves_require_positions_and_sizes_together(kwargs):
    with pytest.raises(ValueError, match="given together"):
        db.create_curves_object(**kwargs)


def test_centroid_boolean_mask():
    bob = db.create_bob(np.array([[0, 0, 0], [2, 0, 0], [10, 10, 10]], dtype=float))
    assert np.allclose(bob.centroid(np.array([True, True, False])), [1, 0, 0])


def test_centroid_unsigned_indices():
    bob = db.create_bob(np.array([[0, 0, 0], [2, 0, 0], [10, 10, 10]], dtype=float))
    assert np.allclose(bob.centroid(np.array([0, 1], dtype=np.uint32)), [1, 0, 0])


def test_centroid_boolean_attribute():
    bob = db.create_bob(np.array([[0, 0, 0], [2, 0, 0], [10, 10, 10]], dtype=float))
    bob.store_named_attribute(np.array([True, True, False]), "selected")
    assert np.allclose(bob.centroid("selected"), [1, 0, 0])


def test_centroid_invalid_weight():
    bob = db.create_bob(np.zeros((3, 3)))
    with pytest.raises(TypeError):
        bob.centroid(np.array(["a", "b", "c"]))
