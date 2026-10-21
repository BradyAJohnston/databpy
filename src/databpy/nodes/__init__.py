"""
Deprecated: node groups are handled by nodebpy (https://pypi.org/project/nodebpy/),
and this module will be removed in databpy 0.14.0.

Importing the module warns with a `FutureWarning`, as does each use of its functions
and classes. `import databpy` doesn't import it.
"""

import importlib
import os
import warnings

from .._deprecation import REMOVAL_VERSION

# point the warning at the code importing this module, skipping the import system and
# databpy's own lazy import of it
warnings.warn(
    f"`databpy.nodes` is deprecated and will be removed in databpy {REMOVAL_VERSION}. "
    "Node groups are handled by nodebpy (https://pypi.org/project/nodebpy/).",
    FutureWarning,
    skip_file_prefixes=(
        os.path.dirname(os.path.dirname(__file__)) + os.sep,
        os.path.dirname(importlib.__file__) + os.sep,
        "<frozen importlib",
    ),
)

from .appending import (
    DuplicatePrevention,
    append_from_blend,
    cleanup_duplicates,
    deduplicate_node_trees,
)
from .generating import custom_string_iswitch, new_tree, swap_tree
from .utils import (
    MaintainConnections,
    NodeGroupCreationError,
    get_input,
    get_output,
    input_socket,
    new_socket,
    output_socket,
    set_socket_value,
    socket_value,
    tree_interface,
)

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
    "input_socket",
    "new_socket",
    "new_tree",
    "output_socket",
    "set_socket_value",
    "socket_value",
    "swap_tree",
    "tree_interface",
]
