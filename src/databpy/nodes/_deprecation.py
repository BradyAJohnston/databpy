import functools
import warnings
from collections.abc import Callable
from typing import overload

REMOVAL_VERSION = "0.12.0"

# depth of nested deprecated calls, so a deprecated function that internally uses
# other deprecated functions only warns once for the user's outermost call
_depth = 0


@overload
def deprecated[T: type](obj: T) -> T: ...


@overload
def deprecated[**P, R](obj: Callable[P, R]) -> Callable[P, R]: ...


def deprecated(obj):
    """Mark a `databpy.nodes` function or class as deprecated.

    Classes warn when instantiated. Only the outermost deprecated call warns.
    """
    target = obj.__init__ if isinstance(obj, type) else obj

    @functools.wraps(target)
    def wrapper(*args, **kwargs):
        global _depth
        if _depth == 0:
            warnings.warn(
                f"`databpy.nodes.{obj.__name__}` is deprecated and will be removed in "
                f"databpy {REMOVAL_VERSION}. Node-related functionality is moving to "
                "nodebpy (https://pypi.org/project/nodebpy/).",
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
