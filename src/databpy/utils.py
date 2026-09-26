from pathlib import Path

import bpy
import numpy as np
from numpy import typing as npt


def require[T](value: T | None, message: str = "Expected a value but got None") -> T:
    """Return the given value, raising an error if it is None.

    Many Blender API accessors are typed as returning `SomeType | None`. This
    helper narrows such values to their non-None type, raising a clear error
    instead of an `AttributeError` further down the line.

    Parameters
    ----------
    value : T | None
        The possibly-None value to check.
    message : str, optional
        The error message to raise if the value is None.

    Returns
    -------
    T
        The value, guaranteed not to be None.

    Raises
    ------
    ValueError
        If the value is None.
    """
    if value is None:
        raise ValueError(message)
    return value


def active_scene(context: bpy.types.Context | None = None) -> bpy.types.Scene:
    """Return the active scene, raising an error if there is none.

    Parameters
    ----------
    context : bpy.types.Context | None, optional
        The context to read the scene from. Defaults to `bpy.context`.

    Returns
    -------
    bpy.types.Scene
        The active scene.

    Raises
    ------
    ValueError
        If the context has no active scene.
    """
    if context is None:
        context = bpy.context
    return require(context.scene, "No active scene in the current context")


def active_object(context: bpy.types.Context | None = None) -> bpy.types.Object:
    """Return the active object, raising an error if there is none.

    Parameters
    ----------
    context : bpy.types.Context | None, optional
        The context to read the active object from. Defaults to `bpy.context`.

    Returns
    -------
    bpy.types.Object
        The active object.

    Raises
    ------
    ValueError
        If the context has no active object.
    """
    if context is None:
        context = bpy.context
    return require(context.active_object, "No active object in the current context")


def require_data[DataBlockT: bpy.types.ID](
    obj: bpy.types.Object, data_type: type[DataBlockT]
) -> DataBlockT:
    """Return the object's data-block, checked to be of the given type.

    `Object.data` can be any of Blender's data-block types (or None), so this
    helper narrows it to the expected type with a proper runtime check.

    Parameters
    ----------
    obj : bpy.types.Object
        The object to get the data-block from.
    data_type : type[DataBlockT]
        The expected type of the data-block (e.g. `bpy.types.Mesh`).

    Returns
    -------
    DataBlockT
        The object's data-block, guaranteed to be of the given type.

    Raises
    ------
    TypeError
        If the object's data is not of the expected type.
    """
    data = obj.data
    if not isinstance(data, data_type):
        raise TypeError(
            f"Data of object '{obj.name}' is {type(data).__name__}, "
            f"expected {data_type.__name__}"
        )
    return data


def mesh_data(obj: bpy.types.Object) -> bpy.types.Mesh:
    """Return the object's data-block, checked to be a `Mesh`."""
    return require_data(obj, bpy.types.Mesh)


def curves_data(obj: bpy.types.Object) -> bpy.types.Curves:
    """Return the object's data-block, checked to be a `Curves`."""
    return require_data(obj, bpy.types.Curves)


def pointcloud_data(obj: bpy.types.Object) -> bpy.types.PointCloud:
    """Return the object's data-block, checked to be a `PointCloud`."""
    return require_data(obj, bpy.types.PointCloud)


def volume_data(obj: bpy.types.Object) -> bpy.types.Volume:
    """Return the object's data-block, checked to be a `Volume`."""
    return require_data(obj, bpy.types.Volume)


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


def lerp(
    a: npt.ArrayLike, b: npt.ArrayLike, t: float | npt.ArrayLike = 0.5
) -> np.ndarray:
    """Linearly interpolate between two values.

    Parameters
    ----------
    a : npt.ArrayLike
        The starting value(s).
    b : npt.ArrayLike
        The ending value(s).
    t : float | npt.ArrayLike, optional
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
    a = np.asarray(a)
    b = np.asarray(b)
    return a + (b - a) * np.asarray(t)


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
    TypeError
        If the path is not a string or Path object.
    """
    if not isinstance(path, (str, Path)):
        raise TypeError(f"Path must be string or Path object, got {type(path)}")

    return Path(bpy.path.abspath(str(path))).resolve()
