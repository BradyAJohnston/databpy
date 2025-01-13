import databpy as db
import bpy
import pytest


def test_collection_missing():
    db.collection.create_collection("Collection")
    bpy.data.collections.remove(bpy.data.collections["Collection"])
    with pytest.raises(KeyError):
        bpy.data.collections["Collection"]
    db.collection.create_collection("Collection")


def test_collection_spam():
    n_coll = len(list(bpy.data.collections.keys()))
    for _ in range(10):
        coll = db.collection.create_collection("Collection")
        assert coll.name == "Collection"
        bob = db.create_bob()
    assert n_coll == len(list(bpy.data.collections.keys()))


def test_collection():
    assert "Collection" in bpy.data.collections
    coll = db.collection.create_collection("Example", parent="Collection")
    assert "Collection.001" not in bpy.data.collections
    assert coll.name == "Example"
    assert coll.name in bpy.data.collections
    assert coll.name in bpy.data.collections["Collection"].children


def test_collection_parent():
    db.collection.create_collection(".MN_data", parent="MolecularNodes")
    assert ".MN_data" not in bpy.context.scene.collection.children
