import re
import time
import warnings
from pathlib import Path
from typing import List

import bpy


def deduplicate_node_trees(node_trees: List[bpy.types.NodeTree]):
    # Compile the regex pattern for matching a suffix of a dot followed by 3 numbers
    node_duplicate_pattern = re.compile(r"\.\d{3}$")
    to_remove: List[bpy.types.GeometryNodeTree] = []

    for node_tree in node_trees:
        # Check if the node tree's name matches the duplicate pattern and is not a "NodeGroup"
        # print(f"{node_tree.name=}")

        for node in node_tree.nodes:
            if not hasattr(node, "node_tree"):
                continue
            tree = node.node_tree  # type: ignore
            if tree.name.startswith("NodeGroup"):
                continue
            if not node_duplicate_pattern.search(tree.name):
                continue

            old_name = tree.name
            # Remove the numeric suffix to get the original name
            name_sans = old_name.rsplit(".", 1)[0]
            replacement = bpy.data.node_groups.get(name_sans)
            if not replacement:
                continue

            # print(f"matched {old_name} with {name_sans}")
            node.node_tree = replacement  # type: ignore
            to_remove.append(bpy.data.node_groups[old_name])

    for tree in to_remove:
        try:
            # remove the data from the blend file
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
