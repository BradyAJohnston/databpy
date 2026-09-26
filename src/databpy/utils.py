from pathlib import Path

import bpy
import numpy as np
import numpy.typing as npt


def centre(position: np.ndarray, weight: np.ndarray | None = None) -> np.ndarray:
    """Calculate the weighted centroid of the vectors.

    Parameters
    ----------
    position : np.ndarray
        Array of position vectors.
    weight : np.ndarray | None, optional
        Array of weights for each position. Default is None.

    Returns
    -------
    np.ndarray
        The weighted centroid of the input vectors.
    """
    if weight is None:
        return np.average(position, axis=0)
    return np.average(position, weights=weight, axis=0)


def lerp(a: npt.ArrayLike, b: npt.ArrayLike, t: float = 0.5) -> np.ndarray:
    """Linearly interpolate between two values.

    Parameters
    ----------
    a : npt.ArrayLike
        The starting value.
    b : npt.ArrayLike
        The ending value.
    t : float, optional
        The interpolation parameter. Default is 0.5.

    Returns
    -------
    np.ndarray
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
    a, b = np.asarray(a), np.asarray(b)
    return a + (b - a) * t


def path_resolve(path: str | Path) -> Path:
    """Resolve a path string or Path object to an absolute Path.

    Parameters
    ----------
    path : str | Path
        The path to resolve, either as a string or Path object.

    Returns
    -------
    Path
        The resolved absolute Path.

    Raises
    ------
    ValueError
        If the path cannot be resolved or is of invalid type.
    """
    if not isinstance(path, (str, Path)):
        # a ValueError rather than TypeError, kept for backwards compatibility
        raise ValueError(f"Path must be string or Path object, got {type(path)}")  # noqa: TRY004

    return Path(bpy.path.abspath(str(path))).resolve()
