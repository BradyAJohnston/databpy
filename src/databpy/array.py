from typing import Self

import bpy
import numpy as np

from .addon import find_by_session_uid, session_token
from .attribute import (
    Attribute,
    AttributeDomains,
    AttributeNotFoundError,
    AttributeTypes,
    _as_typed_attribute,
    _attribute_data,
    _attribute_memory,
    _trigger_data_update,
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


class AttributeArray(np.ndarray):
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

    def __new__(cls, obj: bpy.types.Object, name: str) -> Self:
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
            If the object's data isn't a mesh, curves or point cloud.
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
        arr = np.asarray(attr.as_array()).view(cls)
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

    def __setitem__(self, key, value):
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

    def partition(self, *args, **kwargs):
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
            store_named_attribute(
                obj,
                root.view(np.ndarray),
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
            or not root.flags.c_contiguous
        ):
            return False
        memory = _attribute_memory(_as_typed_attribute(attribute), link.atype)
        if memory is None or memory.shape != root.shape:
            return False

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
