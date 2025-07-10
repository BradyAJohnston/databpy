import bpy
from typing import Union
from pathlib import Path
from .object import ObjectTracker
from .collection import create_collection


def import_vdb(
    file: Union[str, Path], collection: Union[str, bpy.types.Collection, None] = None
) -> bpy.types.Object:
    """
    Imports a VDB file as a Blender volume object.

    Parameters
    ----------
    file : Union[str, Path]
        Path to the VDB file.
    collection : Union[str, bpy.types.Collection, None], optional
        Collection to place the imported volume in. Can be either a collection name,
        an existing collection, or None to use the active collection.

    Returns
    -------
    bpy.types.Object
        A Blender object containing the imported volume data.
    """
    with ObjectTracker() as tracker:
        bpy.ops.object.volume_import(filepath=str(file))
        volume_obj = tracker.latest()

    if collection is not None:
        initial_collection = volume_obj.users_collection[0]
        initial_collection.objects.unlink(volume_obj)

        target_collection = collection
        if isinstance(collection, str):
            target_collection = create_collection(collection)

        target_collection.objects.link(volume_obj)

    return volume_obj
