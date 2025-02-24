import numpy as np
import databpy as db
from databpy import LinkedObjectError, bdo
import bpy
import pytest


def test_creat_obj():
    # Create a mesh object named "MyMesh" in the collection "MyCollection"
    # with vertex locations and bond edges.
    locations = [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0]]
    bonds = [(0, 1), (1, 2), (2, 0)]
    name = "MyMesh"
    my_object = db.create_object(locations, bonds, name=name)

    assert len(my_object.data.vertices) == 3
    assert my_object.name == name
    assert my_object.name != "name"


def test_BlenderObject():
    bob = db.BlenderObject(None)

    with pytest.raises(LinkedObjectError):
        bob.object
    with pytest.raises(LinkedObjectError):
        bob.name
    with pytest.raises(LinkedObjectError):
        bob.name = "testing"

    bob = db.BlenderObject(bdo["Cube"])
    assert bob.name == "Cube"
    bob.name = "NewName"
    with pytest.raises(KeyError):
        bdo["Cube"]
    assert bob.name == "NewName"


def test_set_position():
    bob = db.BlenderObject(bdo["Cube"])
    pos_a = bob.position
    bob.position += 10
    pos_b = bob.position
    assert not np.allclose(pos_a, pos_b)
    assert np.allclose(pos_a, pos_b - 10, rtol=0.1)


def test_centroid():
    bpy.ops.wm.read_factory_settings()
    # Create test object with known vertices
    verts = np.array([[0, 0, 0], [1, 1, 1], [2, 2, 2]])
    bob = db.create_bob(verts, name="TestObject")

    # Test unweighted centroid
    centroid = bob.centroid()
    assert np.allclose(centroid, np.array([1, 1, 1]))
    assert np.allclose(db.centre(verts), np.array([1, 1, 1]))

    # Test weighted centroid with float weights
    weights = np.array([0.5, 0.3, 0.2])
    weighted_centroid = bob.centroid(weights)
    expected = np.average(verts, weights=weights, axis=0)
    assert np.allclose(weighted_centroid, expected)
    assert np.allclose(db.utils.centre(verts, weight=weights), expected)

    # Test centroid with integer index selection
    indices = np.array([0, 1])
    indexed_centroid = bob.centroid(indices)
    expected = np.mean(verts[indices], axis=0)
    assert np.allclose(indexed_centroid, expected)

    # Test centroid with named attribute weights
    db.store_named_attribute(bob.object, weights, "weights")
    named_centroid = bob.centroid("weights")
    expected = np.average(verts, weights=weights, axis=0)
    assert np.allclose(named_centroid, expected)


def test_change_names():
    bob_cube = db.BlenderObject("Cube")
    assert bob_cube.name == "Cube"
    with db.ObjectTracker() as o:
        bpy.ops.mesh.primitive_cylinder_add()
        bob_cyl = db.BlenderObject(o.latest())

    assert bob_cyl.name == "Cylinder"
    assert len(bob_cube) != len(bob_cyl)

    # rename the objects, but separately to the linked BlenderObject, so that the
    # reference will have to be rebuilt from the .uuid when the names don't match
    bpy.data.objects["Cylinder"].name = "Cylinder2"
    bpy.data.objects["Cube"].name = "Cylinder"

    # ensure that the reference to the actul object is updated, so that even if the name has
    # changed the reference is reconnected via the .uuid
    assert len(bob_cube) == 8
    assert bob_cube.name == "Cylinder"
    assert bob_cyl.name == "Cylinder2"


def test_matrix_read_write():
    bob = db.create_bob(np.zeros((5, 3)))
    arr = np.array((5, 4, 4), float)
    arr = np.random.rand(5, 4, 4)

    bob.store_named_attribute(
        data=arr, name="test_matrix", atype=db.AttributeTypes.FLOAT4X4
    )

    assert np.allclose(bob.named_attribute("test_matrix"), arr)
    arr2 = np.random.rand(5, 4, 4)
    bob.store_named_attribute(data=arr2, name="test_matrix2")
    assert (
        bob.object.data.attributes["test_matrix2"].data_type
        == db.AttributeTypes.FLOAT4X4.value.type_name
    )
    assert not np.allclose(bob.named_attribute("test_matrix2"), arr)
