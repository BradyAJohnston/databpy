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

    Raises
    ------
    RuntimeError
        If the VDB file could not be imported (e.g., file not found).
    """
    # Check if file exists
    file_path = Path(file)
    if not file_path.exists():
        raise RuntimeError(f"VDB file not found: {file_path}")

    with ObjectTracker() as tracker:
        bpy.ops.object.volume_import(filepath=str(file))
        new_objects = tracker.new_objects()

        # Check if any objects were created
        if not new_objects:
            raise RuntimeError(f"Failed to import VDB file: {file_path}")

        volume_obj = new_objects[-1]

    if collection is not None:
        initial_collection = volume_obj.users_collection[0]
        initial_collection.objects.unlink(volume_obj)

        target_collection = collection
        if isinstance(collection, str):
            target_collection = create_collection(collection)

        target_collection.objects.link(volume_obj)

    return volume_obj
