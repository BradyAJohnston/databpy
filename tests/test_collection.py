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
        db.create_bob()
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


# New tests to improve coverage


def test_get_collection_existing():
    """Test _get_collection with existing collection."""
    # Create a collection first
    test_coll = bpy.data.collections.new("TestExisting")
    bpy.context.scene.collection.children.link(test_coll)

    # Test that _get_collection returns the existing one
    retrieved = db.collection._get_collection("TestExisting")
    assert retrieved == test_coll
    assert retrieved.name == "TestExisting"


def test_get_collection_new():
    """Test _get_collection creates new collection when it doesn't exist."""
    # Ensure collection doesn't exist
    if "TestNew" in bpy.data.collections:
        bpy.data.collections.remove(bpy.data.collections["TestNew"])

    # Test that _get_collection creates new collection
    new_coll = db.collection._get_collection("TestNew")
    assert new_coll.name == "TestNew"
    assert "TestNew" in bpy.data.collections
    assert new_coll.name in bpy.context.scene.collection.children


def test_create_collection_default_name():
    """Test create_collection with default name."""
    coll = db.collection.create_collection()
    assert coll.name == "NewCollection"
    assert "NewCollection" in bpy.data.collections


def test_create_collection_with_collection_parent():
    """Test create_collection with Collection object as parent."""
    # Create parent collection
    parent_coll = db.collection.create_collection("ParentCollection")

    # Create child with Collection object as parent
    child_coll = db.collection.create_collection("ChildCollection", parent=parent_coll)

    assert child_coll.name == "ChildCollection"
    assert child_coll.name in parent_coll.children
    # Should be unlinked from scene root
    assert child_coll.name not in bpy.context.scene.collection.children


def test_create_collection_with_string_parent():
    """Test create_collection with string parent name."""
    # Create parent collection
    db.collection.create_collection("StringParent")

    # Create child with string parent name
    child_coll = db.collection.create_collection("StringChild", parent="StringParent")

    assert child_coll.name == "StringChild"
    assert child_coll.name in bpy.data.collections["StringParent"].children
    # Should be unlinked from scene root
    assert child_coll.name not in bpy.context.scene.collection.children


def test_create_collection_invalid_parent_type():
    """Test create_collection raises TypeError for invalid parent type."""
    with pytest.raises(TypeError, match="Parent must be a Collection, string or None"):
        db.collection.create_collection("TestCollection", parent=123)

    with pytest.raises(TypeError, match="Parent must be a Collection, string or None"):
        db.collection.create_collection("TestCollection", parent=[])


def test_create_collection_nonexistent_parent_string():
    """Test create_collection with non-existent parent string creates parent."""
    # Ensure parent doesn't exist
    if "NonExistentParent" in bpy.data.collections:
        bpy.data.collections.remove(bpy.data.collections["NonExistentParent"])

    # This should create both parent and child
    child_coll = db.collection.create_collection(
        "ChildOfNonExistent", parent="NonExistentParent"
    )

    assert "NonExistentParent" in bpy.data.collections
    assert child_coll.name == "ChildOfNonExistent"
    assert child_coll.name in bpy.data.collections["NonExistentParent"].children


def test_create_collection_already_in_parent():
    """Test create_collection when collection already exists in parent."""
    # Create parent and child
    parent_coll = db.collection.create_collection("ExistingParent")
    child_coll = db.collection.create_collection("ExistingChild", parent=parent_coll)

    # Try to create the same child again with same parent
    child_coll2 = db.collection.create_collection("ExistingChild", parent=parent_coll)

    # Should return the same collection
    assert child_coll == child_coll2
    assert child_coll.name in parent_coll.children

    # Should only have one instance in parent
    child_count = sum(1 for c in parent_coll.children if c.name == "ExistingChild")
    assert child_count == 1


def test_create_collection_move_from_scene_to_parent():
    """Test that collection is moved from scene root to parent when parent is specified."""
    # Create collection in scene root first
    coll = db.collection.create_collection("MoveTest")
    assert coll.name in bpy.context.scene.collection.children

    # Create parent
    parent_coll = db.collection.create_collection("MoveParent")

    # Move collection to parent
    moved_coll = db.collection.create_collection("MoveTest", parent=parent_coll)

    # Should be the same collection
    assert moved_coll == coll
    # Should be in parent
    assert moved_coll.name in parent_coll.children
    # Should be removed from scene root
    assert moved_coll.name not in bpy.context.scene.collection.children


def test_create_collection_none_parent_explicit():
    """Test create_collection with explicit None parent stays in scene."""
    coll = db.collection.create_collection("ExplicitNone", parent=None)
    assert coll.name == "ExplicitNone"
    assert coll.name in bpy.context.scene.collection.children


def test_create_collection_nested_hierarchy():
    """Test creating nested collection hierarchy."""
    # Create grandparent -> parent -> child hierarchy
    grandparent = db.collection.create_collection("Grandparent")
    parent = db.collection.create_collection("Parent", parent=grandparent)
    child = db.collection.create_collection("Child", parent=parent)

    # Verify hierarchy
    assert parent.name in grandparent.children
    assert child.name in parent.children
    assert grandparent.name in bpy.context.scene.collection.children
    assert parent.name not in bpy.context.scene.collection.children
    assert child.name not in bpy.context.scene.collection.children


def test_create_collection_reuse_existing_with_different_parent():
    """Test that existing collection can be moved to different parent."""
    # Create initial setup
    parent1 = db.collection.create_collection("Parent1")
    parent2 = db.collection.create_collection("Parent2")
    child = db.collection.create_collection("MovableChild", parent=parent1)

    assert child.name in parent1.children
    assert child.name not in parent2.children

    # Move to different parent
    moved_child = db.collection.create_collection("MovableChild", parent=parent2)

    # Should be same collection object
    assert moved_child == child
    # Should be in new parent
    assert moved_child.name in parent2.children
    # Should be removed from old parent (this tests the unlinking logic)
    assert moved_child.name not in bpy.context.scene.collection.children
