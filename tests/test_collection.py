import databpy as db
import bpy
import pytest


def test_collection_missing():
    db.collection.create_collection("Collection")
    bpy.data.collections.remove(bpy.data.collections["Collection"])
    with pytest.raises(KeyError):
        bpy.data.collections["Collection"]
    db.collection.create_collection("Collection")


def test_collection():
    assert "Collection" in bpy.data.collections
    coll = db.collection.create_collection("Example", parent="Collection")
    assert coll.name in bpy.data.collections
    assert coll.name in bpy.data.collections["Collection"].children
