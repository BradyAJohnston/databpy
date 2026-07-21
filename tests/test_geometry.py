import bpy
import numpy as np
import pytest
from nodebpy import geometry as g

import databpy as db


def _add_points_and_instances_nodes(obj: bpy.types.Object) -> None:
    """Add a modifier converting the mesh to points and cube instances."""
    with g.tree("test_gn") as tree:
        geo = tree.inputs.geometry()

        (
            g.JoinGeometry(
                [
                    g.MeshToPoints(geo),
                    g.InstanceOnPoints(geo, instance=g.Cube()),
                ]
            )
            >> tree.outputs.geometry()
        )

    obj.modifiers.new("test_gn", "NODES").node_group = tree.tree


def test_geometry_set_mesh():
    verts = np.array([[0, 0, 0], [1, 1, 1], [2, 2, 2]], dtype=np.float32)
    obj = db.create_object(verts, name="TestObject")

    geom = db.GeometrySet(obj)
    assert geom.mesh is not None
    assert geom.pointcloud is None
    assert geom.instances is None
    assert list(geom.components()) == ["MESH"]
    np.testing.assert_allclose(geom.named_attribute("position"), verts)
    np.testing.assert_allclose(
        geom.named_attribute("position", component="MESH"), verts
    )


def test_geometry_set_multiple_components():
    obj = db.create_object(np.random.rand(4, 3), name="TestObject")
    _add_points_and_instances_nodes(obj)

    geom = db.GeometrySet(obj)
    # the evaluated geometry may contain an empty mesh component, but empty
    # components are excluded from components() and attribute access
    assert list(geom.components()) == ["POINTCLOUD", "INSTANCES"]

    pos = geom.named_attribute("position", component="POINTCLOUD")
    assert pos.shape == (4, 3)

    transforms = geom.named_attribute("instance_transform", component="INSTANCES")
    assert transforms.shape == (4, 4, 4)

    # component=None searches all components for the attribute
    found = geom.named_attribute("instance_transform")
    np.testing.assert_allclose(found, transforms)

    assert len(geom.instance_references) == 1

    listed = geom.list_attributes()
    assert "position" in listed["POINTCLOUD"]
    assert "instance_transform" in listed["INSTANCES"]
    # hidden attributes like .reference_index can be dropped
    hidden_dropped = geom.list_attributes(drop_hidden=True)
    assert not any(
        name.startswith(".") for names in hidden_dropped.values() for name in names
    )


def test_geometry_set_errors():
    obj = db.create_object(np.random.rand(4, 3), name="TestObject")
    geom = db.GeometrySet(obj)

    with pytest.raises(db.NamedAttributeError, match="does not exist on any"):
        geom.named_attribute("nonexistent")

    with pytest.raises(db.NamedAttributeError, match="does not exist on the MESH"):
        geom.named_attribute("nonexistent", component="MESH")

    with pytest.raises(db.NamedAttributeError, match="No POINTCLOUD component"):
        geom.named_attribute("position", component="POINTCLOUD")


def test_geometry_set_repr():
    obj = db.create_object(np.random.rand(4, 3), name="TestObject")
    _add_points_and_instances_nodes(obj)

    text = repr(db.GeometrySet(obj))
    assert "GeometrySet of 'TestObject'" in text
    assert "POINTCLOUD: 4 points" in text
    assert "INSTANCES: 4 points" in text
