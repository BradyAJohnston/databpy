import bpy
from bpy.types import Collection


def _get_collection(name: str) -> Collection:
    """
    Retrieve a Blender collection by name, if it doesn't exist, create it and link to scene.

    Parameters
    ----------
    name : str
        The name of the collection to retrieve or create

    Returns
    -------
    Collection
        The retrieved or created Blender collection
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
    Create a new Blender collection or retrieve an existing one.

    Parameters
    ----------
    name : str, optional
        The name of the collection to create or retrieve. Default is "NewCollection".
    parent : Collection or str or None, optional
        The parent collection to link the new collection to. If a string is provided,
        it will be used to find an existing collection by name. If None, the new collection
        will be linked to the scene's root collection. Default is None.

    Returns
    -------
    Collection
        The created or retrieved Blender collection.

    Raises
    ------
    TypeError
        If the parent parameter is not a Collection, string or None.
    KeyError
        If the parent collection name provided does not exist in bpy.data.collections.
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

def move_to_collection(objs: bpy.types.Object | list[bpy.types.Object], target_collection: bpy.types.Collection) -> None:
    """
    Move one or many objects into a target collection.

    Parameters
    ----------
    objs : bpy.types.Object or list[bpy.types.Object]
        A single object or list of objects to move.
    target_collection : bpy.types.Collection
        The collection to move the objects into.

    Returns
    -------
    None
        This function does not return a value.
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
