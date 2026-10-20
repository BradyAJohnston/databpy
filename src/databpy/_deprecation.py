import functools
import warnings
from collections.abc import Callable
from typing import overload

# the version that removes everything deprecated in databpy
REMOVAL_VERSION = "0.13.0"

# depth of nested deprecated calls, so a deprecated function that internally uses
# other deprecated functions only warns once for the user's outermost call
_depth = 0


def _public_module(module: str) -> str:
    """The module a deprecated object is used from, e.g. `databpy.nodes`."""
    return "databpy.nodes" if module.startswith("databpy.nodes.") else module


@overload
def deprecated[T: type](obj: T) -> T: ...


@overload
def deprecated[**P, R](obj: Callable[P, R]) -> Callable[P, R]: ...


def deprecated(obj):
    """Mark a node or appending function or class as deprecated, in favour of nodebpy.

    Classes warn when instantiated. Only the outermost deprecated call warns.
    """
    target = obj.__init__ if isinstance(obj, type) else obj
    name = f"{_public_module(obj.__module__)}.{obj.__name__}"

    @functools.wraps(target)
    def wrapper(*args, **kwargs):
        global _depth
        if _depth == 0:
            warnings.warn(
                f"`{name}` is deprecated and will be removed in databpy "
                f"{REMOVAL_VERSION}. Node groups and appending from .blend files are "
                "handled by nodebpy (https://pypi.org/project/nodebpy/).",
                FutureWarning,
                stacklevel=2,
            )
        _depth += 1
        try:
            return target(*args, **kwargs)
        finally:
            _depth -= 1

    if isinstance(obj, type):
        obj.__init__ = wrapper
        return obj
    return wrapper
