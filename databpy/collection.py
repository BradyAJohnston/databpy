import bpy
from bpy.types import Collection


def _get_collection(name: str) -> Collection:
    """
    Retrieve a Blender collection by name.
    """
    try:
        return bpy.data.collections[name]
    except KeyError:
        coll = bpy.data.collections.new(name)
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
    KeyError
        If the parent collection name provided does not exist in bpy.data.collections.
    """

    coll = _get_collection(name)
    if parent is None:
        return coll

    if isinstance(parent, str):
        parent = _get_collection(parent)

    if not isinstance(parent, Collection):
        raise TypeError("Parent must be a Collection or a string")

    parent.children.link(coll)
    return coll
