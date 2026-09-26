"""
Deprecated: node-related functionality is moving to nodebpy and this module will be
removed in databpy 0.11.0. Each function warns with a `FutureWarning` when used.
"""

from .appending import (
    DuplicatePrevention,
    append_from_blend,
    cleanup_duplicates,
    deduplicate_node_trees,
)
from .generating import custom_string_iswitch, new_tree, swap_tree
from .utils import MaintainConnections, NodeGroupCreationError, get_input, get_output

__all__ = [
    "DuplicatePrevention",
    "MaintainConnections",
    "NodeGroupCreationError",
    "append_from_blend",
    "cleanup_duplicates",
    "custom_string_iswitch",
    "deduplicate_node_trees",
    "get_input",
    "get_output",
    "new_tree",
    "swap_tree",
]
