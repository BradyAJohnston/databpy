import numpy as np
from pathlib import Path
import bpy


def centre(position: np.ndarray, weight: np.ndarray | None = None):
    "Calculate the weighted centroid of the vectors"
    if weight is None:
        return np.average(position, axis=0)
    return np.average(position, weights=weight, axis=0)


def lerp(a: np.ndarray, b: np.ndarray, t: float = 0.5) -> np.ndarray:
    """
    Linearly interpolate between two values.

    Parameters
    ----------
    a : array_like
        The starting value.
    b : array_like
        The ending value.
    t : float, optional
        The interpolation parameter. Default is 0.5.

    Returns
    -------
    array_like
        The interpolated value(s).

    Notes
    -----
    This function performs linear interpolation between `a` and `b` using the
    interpolation parameter `t` such that the result lies between `a` and `b`.

    Examples
    --------
    ```{python}
    from databpy.utils import lerp
    lerp(1, 2, 0.5)
    lerp(3, 7, 0.2)
    lerp([1, 2, 3], [4, 5, 6], 0.5)
    ```
    """
    return np.add(a, np.multiply(np.subtract(b, a), t))


def path_resolve(path: str | Path) -> Path:
    """
    Resolve a path string or Path object to an absolute Path

    Parameters
    ----------
    path : str or Path
        The path to resolve, either as a string or Path object.

    Returns
    -------
    Path
        The resolved absolute Path.

    Raises
    ------
    ValueError
        If the path cannot be resolved.
    """

    if isinstance(path, str):
        return Path(bpy.path.abspath(path)).absolute()
    elif isinstance(path, Path):
        return Path(bpy.path.abspath(str(path))).absolute()
    else:
        raise ValueError(f"Unable to resolve path: {path}")
