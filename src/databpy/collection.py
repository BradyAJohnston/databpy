import bpy
from bpy.types import Collection


def _get_collection(name: str) -> Collection:
    """
    Get a collection by name, creating it and linking it to the scene if it doesn't exist.

    Parameters
    ----------
    name : str
        The name of the collection to get or create.

    Returns
    -------
    Collection
        The existing or newly created collection.
    """
    if name in bpy.data.collections:
        return bpy.data.collections[name]

    coll = bpy.data.collections.new(name)
    if bpy.context.scene:
        bpy.context.scene.collection.children.link(coll)
    return coll


def create_collection(
    name: str = "NewCollection", parent: Collection | str | None = None
) -> Collection:
    """
    Create a new Blender collection or get an existing one.

    A collection that doesn't exist yet is created and linked to the active scene's
    collection. An existing collection is returned without changing where it is linked,
    unless a parent is given.

    Parameters
    ----------
    name : str, optional
        The name of the collection to create or get. Default is "NewCollection".
    parent : Collection or str or None, optional
        The collection to link the collection into, which also unlinks it from the
        scene's collection. A string is the name of the parent collection, which is
        created and linked to the scene if it doesn't exist. Default is None, which
        leaves the collection where it is.

    Returns
    -------
    Collection
        The created or existing collection.

    Raises
    ------
    TypeError
        If `parent` is not a Collection, string or None.
    """
    if not isinstance(parent, (Collection, str, type(None))):
        raise TypeError("Parent must be a Collection, string or None")

    if isinstance(parent, str):
        parent = _get_collection(parent)

    coll = _get_collection(name)

    if parent is None:
        return coll

    if coll.name in parent.children:
        return coll

    parent.children.link(coll)
    if bpy.context.scene and coll.name in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.unlink(coll)

    return coll


def move_to_collection(
    objs: bpy.types.Object | list[bpy.types.Object],
    target_collection: bpy.types.Collection,
) -> None:
    """
    Move one or many objects into a target collection.

    Parameters
    ----------
    objs : bpy.types.Object or list[bpy.types.Object]
        A single object or list of objects to move.
    target_collection : bpy.types.Collection
        The collection to move the objects into. Each object is unlinked from all
        of the collections it is currently in.
    """
    # Allow single object
    if isinstance(objs, bpy.types.Object):
        objs = [objs]

    for obj in objs:
        # Unlink from all current collections
        for c in obj.users_collection:
            c.objects.unlink(obj)

        # Link to target collection
        target_collection.objects.link(obj)
