"""
Deprecated: node-related functionality is moving to nodebpy and this module will be
removed in databpy 0.11.0. Each function warns with a `FutureWarning` when used.
"""

from .appending import (
    cleanup_duplicates,
    deduplicate_node_trees,
    DuplicatePrevention,
    append_from_blend,
)
from .generating import custom_string_iswitch, new_tree, swap_tree
from .utils import get_input, get_output, MaintainConnections, NodeGroupCreationError

__all__ = [
    "cleanup_duplicates",
    "deduplicate_node_trees",
    "DuplicatePrevention",
    "append_from_blend",
    "custom_string_iswitch",
    "new_tree",
    "swap_tree",
    "get_input",
    "get_output",
    "MaintainConnections",
    "NodeGroupCreationError",
]
