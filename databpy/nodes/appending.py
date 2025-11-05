import re
import time
import warnings
from pathlib import Path
from typing import List

import bpy

from .utils import NODE_DUP_SUFFIX


def deduplicate_node_trees(node_trees: List[bpy.types.NodeTree]):
    """Deduplicate node trees by remapping duplicates to their originals

    This implementation uses user_remap() to automatically update all references
    throughout Blender, then removes the duplicate node trees. It processes in
    three passes to avoid redundant work and ensure correctness.
    """
    node_duplicate_pattern = re.compile(NODE_DUP_SUFFIX)
    to_remove: set[bpy.types.NodeTree] = set()

    # First pass: identify all duplicates and their replacements
    remap_pairs = []

    for node_tree in node_trees:
        # Skip if already marked for removal
        if node_tree in to_remove:
            continue

        old_name = node_tree.name

        if node_duplicate_pattern.search(old_name):
            # Remove the numeric suffix to get the original name
            name_sans = old_name.rsplit(".", 1)[0]
            replacement = bpy.data.node_groups.get(name_sans)

            # Only remap if replacement exists and isn't also marked for removal
            if replacement and replacement not in to_remove:
                remap_pairs.append((node_tree, replacement))
                to_remove.add(node_tree)

    # Second pass: perform all remappings
    for node_tree, replacement in remap_pairs:
        node_tree.user_remap(replacement)

    # Third pass: remove all duplicates
    for tree in to_remove:
        try:
            bpy.data.node_groups.remove(tree)
        except ReferenceError:
            pass


def cleanup_duplicates(purge: bool = False):
    # Collect all node trees from node groups, excluding "NodeGroup" named ones
    node_trees = [tree for tree in bpy.data.node_groups if "NodeGroup" not in tree.name]

    # Call the deduplication function with the collected node trees
    deduplicate_node_trees(node_trees)

    if purge:
        # Purge orphan data blocks from the file
        bpy.ops.outliner.orphans_purge()


class DuplicatePrevention:
    "Context manager to cleanup duplicated node trees when appending node groups"

    def __init__(self, timing=False):
        self.old_names: List[str] = []
        self.start_time: float = 0.0
        self.timing = timing

    def __enter__(self):
        self.old_names = [tree.name for tree in bpy.data.node_groups]
        if self.timing:
            self.start_time = time.time()

    def __exit__(self, type, value, traceback):
        deduplicate_node_trees(
            [tree for tree in bpy.data.node_groups if tree.name not in self.old_names]
        )
        if self.timing:
            end_time = time.time()
            print(f"De-duplication time: {end_time - self.start_time:.2f} seconds")


def append_from_blend(
    name: str, filepath: str | Path, link: bool = False
) -> bpy.types.NodeTree:
    "Append a Geometry Nodes node tree from the given .blend file"
    # to access the nodes we need to specify the "NodeTree" folder but this isn't a real
    # folder, just for accessing when appending. Ensure that the filepath ends with "NodeTree"
    filepath = str(Path(filepath)).removesuffix("NodeTree")
    filepath = str(Path(filepath) / "NodeTree")
    try:
        return bpy.data.node_groups[name]
    except KeyError:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            with DuplicatePrevention():
                # Append from NodeTree directory inside blend file
                bpy.ops.wm.append(
                    "EXEC_DEFAULT",
                    directory=filepath,
                    filename=name,
                    link=link,
                    use_recursive=True,
                )
        return bpy.data.node_groups[name]
