import numpy as np
from .attribute import Attribute, store_named_attribute
import bpy


class AttributeArray(np.ndarray):
    """
    A numpy array subclass that automatically syncs changes back to the Blender object.

    AttributeArray provides an ergonomic interface for working with Blender attributes
    using familiar numpy operations. It automatically handles bidirectional syncing:
    values are retrieved from Blender as a numpy array, operations are applied,
    and results are immediately stored back to Blender.

    This is the high-level interface for attribute manipulation. For low-level control,
    see the `Attribute` class which provides manual get/set operations without auto-sync.

    Performance Characteristics
    ---------------------------
    - Every modification syncs the ENTIRE attribute array to Blender, not just changed values
    - This is due to Blender's foreach_set API requiring the complete array
    - For large meshes (10K+ elements), consider batching multiple operations
    - Example: `pos[:, 2] += 1.0` writes all position data, not just Z coordinates

    Supported Types
    ---------------
    Works with all Blender attribute types:
    - Float types: FLOAT, FLOAT2, FLOAT_VECTOR, FLOAT_COLOR, FLOAT4X4, QUATERNION
    - Integer types: INT (int32), INT8, INT32_2D
    - Boolean: BOOLEAN
    - Color: BYTE_COLOR (uint8)

    Attributes
    ----------
    _blender_object : bpy.types.Object
        Reference to the Blender object for syncing changes.
    _attribute : Attribute
        The underlying Attribute instance with type information.
    _attr_name : str
        Name of the attribute being wrapped.
    _root : AttributeArray
        Reference to the root array for handling views/slices correctly.

    Examples
    --------
    Basic usage:

    ```{python}
    import databpy as db
    import numpy as np

    obj = db.create_object(np.random.rand(10, 3), name="test_bob")
    pos = db.AttributeArray(obj, "position")
    pos[:, 2] += 1.0  # Automatically syncs to Blender
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
    id_array += 100  # Automatically syncs as int32
    ```

    See Also
    --------
    Attribute : Low-level attribute interface without auto-sync
    store_named_attribute : Function to create/update attributes
    named_attribute : Function to read attribute data as regular arrays
    """

    def __new__(cls, obj: bpy.types.Object, name: str) -> "AttributeArray":
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
        """
        attr = Attribute(obj.data.attributes[name])
        arr = np.asarray(attr.as_array()).view(cls)
        arr._blender_object = obj
        arr._attribute = attr
        arr._attr_name = name
        # Track the root array so that views can sync the full data
        arr._root = arr
        return arr

    def __array_finalize__(self, obj):
        """Initialize attributes when array is created through operations."""
        if obj is None:
            return

        self._blender_object = getattr(obj, "_blender_object", None)
        self._attribute = getattr(obj, "_attribute", None)
        self._attr_name = getattr(obj, "_attr_name", None)
        # Preserve reference to the root array for syncing
        self._root = getattr(obj, "_root", self)

    def __setitem__(self, key, value):
        """Set item and sync changes back to Blender."""
        super().__setitem__(key, value)
        self._sync_to_blender()

    def _get_expected_components(self):
        """Get the expected number of components for the attribute type.

        Returns the total number of scalar values per element based on the
        attribute's dimensions. For example, FLOAT_VECTOR (3,) returns 3,
        FLOAT4X4 (4, 4) returns 16.
        """
        dimensions = self._attribute.atype.value.dimensions
        return int(np.prod(dimensions))

    def _ensure_correct_shape(self, data):
        """Ensure data has the correct shape for Blender.

        Handles numpy views that may have lost dimension information and
        reshapes 1D arrays to match the expected attribute dimensions.
        """
        expected_components = self._get_expected_components()
        expected_dims = self._attribute.atype.value.dimensions

        # Reshape 1D to correct dimensionality if needed
        if data.ndim == 1 and len(data) % expected_components == 0:
            n_elements = len(data) // expected_components
            if len(expected_dims) == 1:
                # 1D attribute (FLOAT, INT, BOOLEAN, etc.)
                return data
            else:
                # Multi-dimensional attribute
                return data.reshape(n_elements, *expected_dims)

        # Handle views that lost shape information (e.g., column slices)
        if data.ndim != len(self._attribute.shape):
            # Try to get the full array from the root
            full_array = np.asarray(self._root).view(np.ndarray).copy()
            if full_array.shape == self._attribute.shape:
                return full_array

        return data

    def _sync_to_blender(self):
        """Sync the current array data back to the Blender object.

        Note: This syncs the ENTIRE array to Blender on every modification,
        even for single element changes. This is due to Blender's foreach_set
        API requiring the full array. For large meshes, consider batching
        multiple modifications before triggering a sync.
        """
        if self._blender_object is None:
            import warnings

            warnings.warn(
                "AttributeArray has lost its Blender object reference. "
                "Changes will not be synced back to Blender. This can happen "
                "if the array was created from a deleted object or copied incorrectly.",
                RuntimeWarning,
                stacklevel=3,
            )
            return

        # Always sync using the root array to ensure full shape
        root = getattr(self, "_root", self)
        data_to_sync = np.asarray(root).view(np.ndarray)
        data_to_sync = self._ensure_correct_shape(data_to_sync)

        # Use the attribute's actual dtype instead of hardcoding float32
        expected_dtype = self._attribute.dtype
        if data_to_sync.dtype != expected_dtype:
            data_to_sync = data_to_sync.astype(expected_dtype)

        store_named_attribute(
            self._blender_object,
            data_to_sync,
            name=self._attr_name,
            atype=self._attribute.atype,
            domain=self._attribute.domain.name,
        )

    def _inplace_operation_with_sync(self, operation, other):
        """Common method for in-place operations."""
        result = operation(other)
        self._sync_to_blender()
        return result

    def __iadd__(self, other):
        """In-place addition with Blender syncing."""
        return self._inplace_operation_with_sync(super().__iadd__, other)

    def __isub__(self, other):
        """In-place subtraction with Blender syncing."""
        return self._inplace_operation_with_sync(super().__isub__, other)

    def __imul__(self, other):
        """In-place multiplication with Blender syncing."""
        return self._inplace_operation_with_sync(super().__imul__, other)

    def __itruediv__(self, other):
        """In-place division with Blender syncing."""
        return self._inplace_operation_with_sync(super().__itruediv__, other)

    def __str__(self):
        """String representation showing attribute info and array data."""
        # Get basic info
        attr_name = getattr(self, "_attr_name", "Unknown")
        domain = getattr(self._attribute, "domain", None)
        domain_name = domain.name if domain else "Unknown"

        # Get object info
        obj_name = "Unknown"
        obj_type = "Unknown"
        if self._blender_object:
            obj_name = getattr(self._blender_object, "name", "Unknown")
            obj_type = getattr(self._blender_object.data, "name", "Unknown")

        # Get array info
        array_str = np.array_str(np.asarray(self).view(np.ndarray))

        return (
            f"AttributeArray '{attr_name}' from {obj_type}('{obj_name}')"
            f"(domain: {domain_name}, shape: {self.shape}, dtype: {self.dtype})\n"
            f"{array_str}"
        )

    def __repr__(self):
        """Detailed representation for debugging."""
        # Get basic info
        attr_name = getattr(self, "_attr_name", "Unknown")
        domain = getattr(self._attribute, "domain", None)
        domain_name = domain.name if domain else "Unknown"
        atype = getattr(self._attribute, "atype", "Unknown")

        # Get object info
        obj_name = "Unknown"
        obj_type = "Unknown"
        if self._blender_object:
            obj_name = getattr(self._blender_object, "name", "Unknown")
            obj_type = getattr(self._blender_object.data, "name", "Unknown")

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
            f"domain={domain_name}, type={atype.value}, shape={self.shape}, dtype={self.dtype})\n"
            f"{array_repr}"
        )
