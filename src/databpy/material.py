from pathlib import Path

import bpy
from bpy.types import Material

from ._deprecation import deprecated


@deprecated
def append_from_blend(name: str, filepath: str) -> Material:
    """
    Append a material from a .blend file, or get it if it is already loaded.

    Deprecated: appending from .blend files is handled by
    [nodebpy](https://pypi.org/project/nodebpy/), and this will be removed in databpy
    0.13.0.

    Parameters
    ----------
    name : str
        The name of the material.
    filepath : str
        Path to the .blend file containing the material.

    Returns
    -------
    Material
        The material named `name`. If one is already loaded, it is returned without
        appending from the file.

    Raises
    ------
    FileNotFoundError
        If `filepath` doesn't exist, even when the material is already loaded.
    KeyError
        If the file has no material named `name`.

    Warns
    -----
    FutureWarning
        Always, as the function is deprecated.
    """
    file_path = Path(filepath)
    if not file_path.exists():
        raise FileNotFoundError(f"Given file not found: {filepath}")
    try:
        return bpy.data.materials[name]
    except KeyError:
        bpy.ops.wm.append(
            directory=str(file_path / "Material"),
            filename=name,
            link=False,
        )
        return bpy.data.materials[name]
