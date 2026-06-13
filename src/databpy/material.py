from pathlib import Path

import bpy
from bpy.types import Material


# TODO: use DuplicatePrevention when adding material node trees
def append_from_blend(name: str, filepath: str) -> Material:
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
