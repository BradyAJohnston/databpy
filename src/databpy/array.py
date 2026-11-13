from collections.abc import Callable
from typing import Any, ClassVar, Self

import bpy
import numpy as np
import numpy.typing as npt

from .addon import find_by_session_uid, session_token
from .attribute import (
    Attribute,
    AttributeDomains,
    AttributeNotFoundError,
    AttributeTypes,
    _as_typed_attribute,
    _attribute_data,
    _attribute_memory,
    _check_storable,
    _trigger_data_update,
    _value_shape,
    store_named_attribute,
)
from .errors import LinkedObjectError


class _AttributeLink:
    """Session-stable link from an AttributeArray to the attribute it was read from.

    The object is tracked by its `session_uid` rather than a direct reference, which
    can become invalid when Blender reallocates or renames the object.
    """

    def __init__(self, obj: bpy.types.Object, attribute: Attribute):
        self.object_name: str = obj.name
        self.session_uid: int = obj.session_uid
        self.session_token: str = session_token()
        self.name: str = attribute.name
        self.atype: AttributeTypes = attribute.atype
        self.domain: AttributeDomains = attribute.domain
        # converts the array's values to how they are stored, for arrays such as
        # `srgb` whose values aren't stored as they are
        self.encode: Callable[[np.ndarray], np.ndarray] | None = None

    def resolve(self) -> bpy.types.Object:
        if self.session_token != session_token():
            raise LinkedObjectError(
                f"AttributeArray '{self.name}' was read from '{self.object_name}' before "
                "a file was loaded, and can no longer be synced to Blender."
            )
        obj = find_by_session_uid(self.session_uid, self.object_name)
        if obj is None:
            raise LinkedObjectError(
                f"The object '{self.object_name}' for AttributeArray '{self.name}' has "
                "been removed."
            )
        self.object_name = obj.name
        return obj


# numpy functions that write into their first argument without going through a ufunc,
# `__setitem__` or one of the synced methods
_WRITING_FUNCTIONS = {np.copyto, np.place, np.putmask, np.fill_diagonal}


class AttributeArray[ShapeT: tuple[Any, ...], DTypeT: np.dtype[Any]](
    np.ndarray[ShapeT, DTypeT]
):
    """
    A numpy array of an attribute's values that writes changes back to Blender.

    Creating the array reads the attribute's values. Modifying the array in place
    writes the changed values back to the attribute straight away. For manual control
    over when values are read and written, use `Attribute`.

    Syncing
    -------
    Changes are written back to Blender by item assignment (`pos[0] = ...`), in-place
    operators (`pos += 1`, `pos[:, 2] *= 2`), ufuncs with `out=` or `.at`, the
    `fill`, `sort`, `put` and `partition` methods, and `np.copyto`, `np.place`,
    `np.putmask` and `np.fill_diagonal`. Writes through `.flat` are not synced.

    Other operations (`pos + 1`, `pos.copy()`, `pos[mask]`) return plain or detached
    arrays that don't sync. If the object is removed, or a file is loaded, syncing
    raises a `LinkedObjectError`.

    Performance Characteristics
    ---------------------------
    - Creating the array copies all of the attribute's values.
    - Each modification writes only the values it changed, directly into the
      attribute's memory: `pos[:10, 2] = 1.0` writes 10 values however large the
      attribute is.
    - Where the attribute can't be written directly, the entire array is written
      with `store_named_attribute` instead. This applies to STRING attributes, a
      `SINGLE` value for the whole domain, and an attribute that was removed (which is
      re-created). If the attribute's size, type or domain changed since the array
      was read, this raises a `NamedAttributeError`.

    Supported Types
    ---------------
    Every attribute type in `AttributeTypes`, with values in its storage dtype:
    - Float types (float32): FLOAT, FLOAT2, FLOAT4 (Blender 5.2+), FLOAT_VECTOR,
      FLOAT_COLOR, FLOAT4X4, QUATERNION
    - Integer types: INT (int32), INT8, INT16_2D (int16), INT32_2D (int32)
    - Boolean: BOOLEAN
    - Color: BYTE_COLOR (uint8)
    - String: STRING (str), read and written one value at a time

    Attributes
    ----------
    _link : _AttributeLink | None
        Link to the Blender object and attribute, or None for detached copies.
    _root : AttributeArray | None
        The array read from Blender that this array is a view of, or None if this is
        that array (or a detached copy).

    Examples
    --------
    Basic usage:

    ```{python}
    import databpy as db
    import numpy as np

    obj = db.create_object(np.random.rand(10, 3), name="test_bob")
    pos = db.AttributeArray(obj, "position")
    pos[:, 2] += 1.0  # writes the new z values to Blender
    ```

    Using BlenderObject for convenience:

    ```{python}
    import databpy as db
    import numpy as np

    bob = db.create_bob(np.random.rand(10, 3), name="test_bob")
    print('Initial position:')
    print(bob.position)  # Returns an AttributeArray
    ```
    ```{python}
    bob.position[:, 2] += 1.0
    print('Updated position:')
    print(bob.position)
    ```
    ```{python}
    # Convert to regular numpy array (no sync)
    print('As Array:')
    print(np.asarray(bob.position))
    ```

    Working with integer attributes:

    ```{python}
    import databpy as db
    import numpy as np

    obj = db.create_object(np.random.rand(10, 3))
    # Store integer attribute
    ids = np.arange(10, dtype=np.int32)
    db.store_named_attribute(obj, ids, "id", atype="INT")

    # Access as AttributeArray
    id_array = db.AttributeArray(obj, "id")
    id_array += 100  # stays int32 and writes to Blender
    ```

    See Also
    --------
    Attribute : Low-level attribute interface without automatic syncing
    store_named_attribute : Create or update an attribute
    named_attribute : Read an attribute's values as a plain numpy array
    """

    # the attribute type of a typed subclass such as `vec3`, None for this base class
    atype: ClassVar[AttributeTypes | None] = None
    # whether the values are converted when stored and read, as for `srgb`
    _converted: ClassVar[bool] = False

    @staticmethod
    def _encode(values: np.ndarray) -> np.ndarray:
        """Convert values to how they are stored in Blender."""
        return values

    @staticmethod
    def _decode(values: np.ndarray) -> np.ndarray:
        """Convert values stored in Blender to the values of this array type."""
        return values

    def __new__(cls, obj: bpy.types.Object, name: str) -> "AttributeArray[Any, Any]":
        """Create a new AttributeArray that wraps a Blender attribute.

        Parameters
        ----------
        obj : bpy.types.Object
            The Blender object containing the attribute.
        name : str
            The name of the attribute to wrap.

        Returns
        -------
        AttributeArray
            A numpy array subclass that syncs changes back to Blender.

        Raises
        ------
        AttributeNotFoundError
            If the attribute doesn't exist on the object.
        TypeError
            If the object's data isn't a mesh, curves, point cloud or grease pencil.
        NamedAttributeError
            If the attribute has an unsupported data type.
        """
        data = _attribute_data(obj)
        try:
            attr = Attribute(data.attributes[name])
        except KeyError:
            raise AttributeNotFoundError(
                f"The attribute '{name}' does not exist on '{obj.name}'. "
                f"Available attributes: {sorted(data.attributes.keys())}"
            ) from None
        # the array is the typed subclass for the attribute's type, such as `vec3`
        arr = np.asarray(attr.as_array()).view(ARRAY_TYPES[attr.atype])
        arr._link = _AttributeLink(obj, attr)
        return arr

    @property
    def _blender_object(self) -> bpy.types.Object | None:
        """The linked Blender object, or None for detached copies."""
        return None if self._link is None else self._link.resolve()

    def __array_finalize__(self, obj):
        """Link views to the attribute they were read from, and detach copies."""
        if obj is None:
            return

        # only views that still share memory with the source stay connected to
        # Blender; copies (e.g. `pos.copy()`, `pos[mask]`) become detached arrays
        # that no longer sync
        if np.may_share_memory(self, obj):
            self._link = getattr(obj, "_link", None)
            # views refer to the root array, which never refers to itself or its views,
            # so arrays are freed as soon as they are unused rather than waiting for
            # the garbage collector
            root = getattr(obj, "_root", None)
            if root is None and isinstance(obj, AttributeArray):
                root = obj
            self._root = root
        else:
            self._link = None
            self._root = None

    @property
    def _root_array(self) -> "AttributeArray":
        """The array read from Blender that this array is a view of."""
        return self if self._root is None else self._root

    def __array_wrap__(self, out_arr, context=None, return_scalar=False):
        """Return plain numpy arrays from operations that produce new arrays."""
        if out_arr is self:
            return out_arr
        if return_scalar:
            return out_arr[()]
        return np.asarray(out_arr)

    def __array_ufunc__(self, ufunc, method, *inputs, out=None, **kwargs):
        """Run ufuncs on plain arrays, syncing any AttributeArray written to.

        In-place operators (`pos += 1`) are ufuncs with `out=`, so they are synced
        here along with explicit `out=` arguments and `ufunc.at`.
        """
        written = tuple(out) if out is not None else ()
        if method == "at":
            written = inputs[:1]

        inputs = tuple(
            x.view(np.ndarray) if isinstance(x, AttributeArray) else x for x in inputs
        )
        if out is not None:
            kwargs["out"] = tuple(
                x.view(np.ndarray) if isinstance(x, AttributeArray) else x for x in out
            )
        result = getattr(ufunc, method)(*inputs, **kwargs)

        for arr in written:
            if isinstance(arr, AttributeArray):
                arr._sync_to_blender()

        if out is None or method == "at":
            return result
        return out[0] if len(out) == 1 else out

    def __array_function__(self, func, types, args, kwargs):
        """Sync after numpy functions that write into an AttributeArray."""
        result = super().__array_function__(func, types, args, kwargs)
        if func in _WRITING_FUNCTIONS:
            target = args[0] if args else next(iter(kwargs.values()), None)
            if isinstance(target, AttributeArray):
                target._sync_to_blender()
        return result

    def __setitem__(self, key, value):  # ty: ignore[invalid-method-override]
        """Set the values at `key` and write them to Blender."""
        if self._is_writeback(key, value):
            # `pos[:, 2] += 1` assigns the already modified and synced view back to
            # itself, so there is nothing to write
            return
        super().__setitem__(key, value)
        self._sync_to_blender(key)

    def _is_writeback(self, key, value) -> bool:
        if (
            not isinstance(value, AttributeArray)
            or value._link is None
            or value._root_array is not self._root_array
        ):
            return False
        try:
            target = super().__getitem__(key)
        except (IndexError, TypeError, ValueError):
            return False
        return (
            isinstance(target, np.ndarray)
            and target.__array_interface__["data"] == value.__array_interface__["data"]
            and target.shape == value.shape
            and target.strides == value.strides
        )

    def fill(self, value):
        """Fill the array with a scalar value and sync to Blender."""
        super().fill(value)
        self._sync_to_blender()

    def sort(self, *args, **kwargs):
        """Sort the array in-place and sync to Blender."""
        super().sort(*args, **kwargs)
        self._sync_to_blender()

    def put(self, *args, **kwargs):
        """Set values at the given flat indices and sync to Blender."""
        super().put(*args, **kwargs)
        self._sync_to_blender()

    def partition(self, *args, **kwargs):  # ty: ignore[invalid-method-override]
        """Partition the array in-place and sync to Blender."""
        super().partition(*args, **kwargs)
        self._sync_to_blender()

    def _sync_to_blender(self, key=None):
        """Sync the values of this array, or `self[key]`, back to the Blender object.

        Only the changed values are written, directly into the attribute's memory. If
        the attribute can't be written directly, the entire root array is written with
        `store_named_attribute` instead, which also re-creates an attribute that was
        removed.
        """
        link = self._link
        if link is None:
            # a detached copy with no linked attribute; nothing to sync
            return

        obj = link.resolve()
        root = self._root_array
        if not self._write_directly(obj, link, root, key):
            values = root.view(np.ndarray)
            store_named_attribute(
                obj,
                values if link.encode is None else link.encode(values),
                name=link.name,
                atype=link.atype,
                domain=link.domain,
            )

    def _write_directly(
        self, obj: bpy.types.Object, link: _AttributeLink, root: "AttributeArray", key
    ) -> bool:
        """Write the values of this array, or `self[key]`, into the attribute's memory.

        Returns False without writing anything if the attribute can't be written
        directly, or no longer matches the array that was read from it.
        """
        obj_data = _attribute_data(obj)
        attribute = obj_data.attributes.get(link.name)
        if (
            attribute is None
            or attribute.data_type != link.atype.value.type_name
            or attribute.domain != link.domain.value
            or self.dtype != root.dtype
        ):
            return False
        memory = _attribute_memory(_as_typed_attribute(attribute), link.atype)
        if memory is None:
            return False
        # the root array must be laid out like Blender's memory, which FLOAT4X4 arrays
        # read from Blender are as transposed views of the column-major matrices
        layout = memory
        if link.atype == AttributeTypes.FLOAT4X4:
            layout = np.swapaxes(memory, -1, -2)
        if layout.shape != root.shape or layout.strides != root.strides:
            return False

        if link.encode is not None:
            # a view doesn't know which channels it holds, which can be converted
            # differently, so the whole array is converted and written
            layout[...] = link.encode(root.view(np.ndarray))
            _trigger_data_update(obj_data)
            return True

        # this array is a view into the root array, so the same view into Blender's
        # memory covers exactly the values this array holds
        values = self.view(np.ndarray)
        offset = (
            values.__array_interface__["data"][0] - root.__array_interface__["data"][0]
        )
        target = np.ndarray(
            values.shape,
            dtype=values.dtype,
            buffer=memory,
            offset=offset,
            strides=values.strides,
        )

        if key is None:
            target[...] = values
        else:
            target[key] = values[key]
        _trigger_data_update(obj_data)
        return True

    def _describe(self) -> tuple[str, str, str, str, str]:
        """Names of the attribute, domain, type, object and data-block for printing."""
        link = self._link
        if link is None:
            return ("Unknown", "Unknown", "Unknown", "Unknown", "Unknown")
        obj_name = obj_type = "Unknown"
        try:
            obj = link.resolve()
            obj_name, obj_type = obj.name, obj.data.name
        except LinkedObjectError:
            obj_name = link.object_name
        return link.name, link.domain.name, str(link.atype.value), obj_name, obj_type

    def __str__(self):
        """String representation showing attribute info and array data."""
        attr_name, domain_name, _, obj_name, obj_type = self._describe()
        array_str = np.array_str(np.asarray(self).view(np.ndarray))

        return (
            f"AttributeArray '{attr_name}' from {obj_type}('{obj_name}')"
            f"(domain: {domain_name}, shape: {self.shape}, dtype: {self.dtype})\n"
            f"{array_str}"
        )

    def __repr__(self):
        """Detailed representation for debugging."""
        attr_name, domain_name, type_name, obj_name, obj_type = self._describe()

        # Get array representation with explicit dtype for cross-platform consistency
        # np.array_repr() can omit dtype on Windows when it's the platform default
        arr = np.asarray(self).view(np.ndarray)
        # Use np.array_repr() but then ensure dtype is always appended
        array_repr = np.array_repr(arr)
        # If dtype isn't already in the repr, add it before the closing parenthesis
        if f"dtype={arr.dtype}" not in array_repr:
            array_repr = array_repr.rstrip(")") + f", dtype={arr.dtype})"

        return (
            f"AttributeArray(name='{attr_name}', object='{obj_name}', mesh='{obj_type}', "
            f"domain={domain_name}, type={type_name}, shape={self.shape}, dtype={self.dtype})\n"
            f"{array_repr}"
        )


class _TypedArray[ShapeT: tuple[Any, ...], DTypeT: np.dtype[Any]](
    AttributeArray[ShapeT, DTypeT]
):
    """Base for arrays that declare the attribute type they are stored as."""

    atype: ClassVar[AttributeTypes]
    # the shape of a single value, () for single values
    _value_shape: ClassVar[tuple[int, ...]]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._value_shape = _value_shape(cls.atype)

    def __getitem__(self, key):  # ty: ignore[invalid-method-override]
        """Index the array, keeping this type only while it has that shape."""
        out = super().__getitem__(key)
        # `vec[:, 0]` is still a view that syncs, but no longer an array of vectors.
        # Assigning the class avoids `view()` re-running `__array_finalize__`.
        if type(out) is type(self) and (
            out.ndim != 1 + len(self._value_shape) or out.shape[1:] != self._value_shape
        ):
            out.__class__ = AttributeArray
        return out

    def __new__(cls, data: npt.ArrayLike) -> Self:
        """
        Wrap values as an array of this attribute type, ready to be stored.

        The values are only copied if they need casting to the storage dtype.

        Parameters
        ----------
        data : npt.ArrayLike
            The values, with one value per element of the domain they will be stored
            on, or a single value such as `db.color([1, 0.5, 0, 1])` to store for
            every element.

        Raises
        ------
        ValueError
            If the data doesn't have the shape of an array of this type, or of one
            value of it.
        AttributeMismatchError
            If the values can't be represented by this type.
        """
        arr = np.asarray(data)
        value_shape = cls._value_shape
        if arr.shape != value_shape and (
            arr.ndim != 1 + len(value_shape) or arr.shape[1:] != value_shape
        ):
            expected = ("N", *value_shape)
            raise ValueError(
                f"`{cls.__name__}` needs data of shape ({', '.join(map(str, expected))}"
                f"{',' if not value_shape else ''}), or {value_shape} for a single "
                f"value, not {arr.shape}."
            )
        if cls.atype != AttributeTypes.STRING:
            _check_storable(arr, cls.atype)
        # a plain view, so that wrapping an AttributeArray gives an unlinked array
        return arr.astype(cls.atype.value.dtype, copy=False).view(np.ndarray).view(cls)


def _srgb_to_linear(values: np.ndarray) -> np.ndarray:
    """Convert sRGB RGBA colors to linear, leaving alpha as it is."""
    out = np.array(values, dtype=np.float32)
    rgb = out[..., :3]
    # the linear segment is extended below 0, so negative values convert both ways
    curve = ((np.maximum(rgb, 0.04045) + 0.055) / 1.055) ** 2.4
    out[..., :3] = np.where(rgb < 0.04045, rgb / 12.92, curve)
    return out


def _linear_to_srgb(values: np.ndarray) -> np.ndarray:
    """Convert linear RGBA colors to sRGB, leaving alpha as it is."""
    out = np.array(values, dtype=np.float32)
    rgb = out[..., :3]
    curve = 1.055 * np.maximum(rgb, 0.0031308) ** (1 / 2.4) - 0.055
    out[..., :3] = np.where(rgb < 0.0031308, rgb * 12.92, curve)
    return out


def _hex_to_bytes(codes: np.ndarray) -> np.ndarray:
    """Parse hex color codes such as '#FF8000' to RGBA bytes, with alpha 255 if unset."""
    out = np.empty((*codes.shape, 4), dtype=np.uint8)
    for index, code in np.ndenumerate(codes):
        digits = str(code).removeprefix("#")
        if len(digits) in (3, 4):
            digits = "".join(digit * 2 for digit in digits)
        if len(digits) == 6:
            digits += "ff"
        if len(digits) != 8 or any(d not in "0123456789abcdefABCDEF" for d in digits):
            raise ValueError(
                f"`{code}` isn't a hex color code such as '#RGB', '#RGBA', '#RRGGBB' "
                "or '#RRGGBBAA'."
            )
        out[index] = [int(digits[i : i + 2], 16) for i in range(0, 8, 2)]
    return out


def _is_text(data: npt.ArrayLike) -> bool:
    return isinstance(data, str) or np.asarray(data).dtype.kind == "U"


def _as_converted[T: AttributeArray](arr: AttributeArray, cls: type[T]) -> T:
    """Convert an array read from Blender to `cls`, which converts it back on sync."""
    values = arr.view(np.ndarray)
    values[...] = cls._decode(values)
    arr.__class__ = cls
    if arr._link is not None:
        arr._link.encode = cls._encode
    return arr  # ty: ignore[invalid-return-type]


type _Shape1 = tuple[int]
type _Shape2 = tuple[int, int]
type _Shape3 = tuple[int, int, int]
type _Float32 = np.dtype[np.float32]
type _Int32 = np.dtype[np.int32]


class float32(_TypedArray[_Shape1, _Float32]):
    """A `FLOAT` attribute: one float32 value per element."""

    atype = AttributeTypes.FLOAT


class vec2(_TypedArray[_Shape2, _Float32]):
    """A `FLOAT2` attribute: a 2D float32 vector per element."""

    atype = AttributeTypes.FLOAT2


class vec3(_TypedArray[_Shape2, _Float32]):
    """A `FLOAT_VECTOR` attribute: a 3D float32 vector per element."""

    atype = AttributeTypes.FLOAT_VECTOR


class vec4(_TypedArray[_Shape2, _Float32]):
    """A `FLOAT4` attribute: a 4D float32 vector per element (Blender 5.2+)."""

    atype = AttributeTypes.FLOAT4


class color(_TypedArray[_Shape2, _Float32]):
    """A `FLOAT_COLOR` attribute: a linear RGBA float32 color per element."""

    atype = AttributeTypes.FLOAT_COLOR


class srgb(_TypedArray[_Shape2, _Float32]):
    """
    A `FLOAT_COLOR` attribute as sRGB RGBA float32 colors.

    Blender stores color attributes as linear colors. The values of this array are
    sRGB, and are converted to linear when they are stored, and from linear when they
    are read as `bob["name", db.srgb]`. Alpha isn't converted. Results of math on an
    `srgb` array are also `srgb` arrays, so that they are still converted when
    stored.
    """

    atype = AttributeTypes.FLOAT_COLOR
    _converted = True

    def __new__(cls, data: npt.ArrayLike) -> Self:
        """
        Wrap sRGB colors, ready to be stored as linear colors.

        Parameters
        ----------
        data : npt.ArrayLike
            RGBA colors with shape (N, 4), or a single color with shape (4,). Hex
            codes such as '#FF8000', or a list of them, are also accepted.

        Raises
        ------
        ValueError
            If the data doesn't have the shape of RGBA colors, or isn't a valid hex
            code.
        """
        if _is_text(data):
            data = _hex_to_bytes(np.asarray(data)) / np.float32(255)
        return super().__new__(cls, data)

    @staticmethod
    def _encode(values: np.ndarray) -> np.ndarray:
        return _srgb_to_linear(values)

    @staticmethod
    def _decode(values: np.ndarray) -> np.ndarray:
        return _linear_to_srgb(values)

    def __array_ufunc__(self, ufunc, method, *inputs, out=None, **kwargs):
        """Keep the results of elementwise math as sRGB colors."""
        result = super().__array_ufunc__(ufunc, method, *inputs, out=out, **kwargs)
        if (
            out is None
            and method == "__call__"
            and isinstance(result, np.ndarray)
            and result.dtype.kind == "f"
            and result.shape == self.shape
        ):
            return result.astype(np.float32, copy=False).view(srgb)
        return result


class color8(_TypedArray[_Shape2, np.dtype[np.uint8]]):
    """
    A `BYTE_COLOR` attribute: an sRGB RGBA uint8 color per element.

    Hex codes such as '#FF8000', or a list of them, can be wrapped as well.
    """

    atype = AttributeTypes.BYTE_COLOR

    def __new__(cls, data: npt.ArrayLike) -> Self:
        if _is_text(data):
            data = _hex_to_bytes(np.asarray(data))
        return super().__new__(cls, data)


class quat(_TypedArray[_Shape2, _Float32]):
    """A `QUATERNION` attribute: a (w, x, y, z) float32 rotation per element."""

    atype = AttributeTypes.QUATERNION


class mat4(_TypedArray[_Shape3, _Float32]):
    """A `FLOAT4X4` attribute: a row-major 4x4 float32 matrix per element."""

    atype = AttributeTypes.FLOAT4X4


class int32(_TypedArray[_Shape1, _Int32]):
    """An `INT` attribute: one int32 value per element."""

    atype = AttributeTypes.INT


class int8(_TypedArray[_Shape1, np.dtype[np.int8]]):
    """An `INT8` attribute: one int8 value per element."""

    atype = AttributeTypes.INT8


class sivec2(_TypedArray[_Shape2, np.dtype[np.int16]]):
    """An `INT16_2D` attribute: a 2D int16 vector per element."""

    atype = AttributeTypes.INT16_2D


class ivec2(_TypedArray[_Shape2, _Int32]):
    """An `INT32_2D` attribute: a 2D int32 vector per element."""

    atype = AttributeTypes.INT32_2D


class boolean(_TypedArray[_Shape1, np.dtype[np.bool]]):
    """A `BOOLEAN` attribute: one bool per element."""

    atype = AttributeTypes.BOOLEAN


class string(_TypedArray[_Shape1, np.dtype[np.str_]]):
    """A `STRING` attribute: one string per element."""

    atype = AttributeTypes.STRING


ARRAY_TYPES: dict[AttributeTypes, type[AttributeArray]] = {
    cls.atype: cls
    for cls in (
        float32,
        vec2,
        vec3,
        vec4,
        color,
        color8,
        quat,
        mat4,
        int32,
        int8,
        sivec2,
        ivec2,
        boolean,
        string,
    )
}
