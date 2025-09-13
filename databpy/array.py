import numpy as np
from .attribute import Attribute, AttributeTypes, store_named_attribute
import bpy


class AttributeArray(np.ndarray):
    """
    A numpy array subclass that automatically syncs changes back to the Blender object.

    Values are retrieved from the Blender object as a numpy array, the operation is applied
    and the result is store back on the Blender object.
    This allows for operations like `pos[:, 2] += 1.0` to work seamlessly.

    Examples:
    --------
    ```{python}
    import databpy as db
    import numpy as np

    obj = db.create_object(np.random.rand(10, 3), name="test_bob")
    db.AttributeArray(obj, "position")
    ```

    ```{python}
    import databpy as db
    import numpy as np

    bob = db.create_bob(np.random.rand(10, 3), name="test_bob")
    print('Initial position:')
    print(bob.position)  # Access the position attribute as an AttributeArray
    bob.position[:, 2] += 1.0
    print('Updated position:')
    print(bob.position)

    print('As Array:')
    print(np.asarray(bob.position))  # Convert to a regular numpy array
    ```
    """

    def __new__(cls, obj: bpy.types.Object, name: str) -> "AttributeArray":
        """Create a new AttributeArray that wraps a Blender attribute."""
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
        """Get the expected number of components for the attribute type."""
        if self._attribute.atype == AttributeTypes.FLOAT_COLOR:
            return 4
        elif self._attribute.atype == AttributeTypes.FLOAT_VECTOR:
            return 3
        return None

    def _ensure_correct_shape(self, data):
        """Ensure data has the correct shape for Blender."""
        expected_components = self._get_expected_components()
        if expected_components is None:
            return data

        # Reshape 1D to 2D if needed
        if data.ndim == 1 and len(data) % expected_components == 0:
            return data.reshape(-1, expected_components)

        # Handle incorrect column count
        if (
            data.ndim == 2
            and data.shape[1] != expected_components
            and data.shape[1] == 1
        ):
            # Try to get the full array
            full_array = np.asarray(self).view(np.ndarray).copy()
            if full_array.shape[1] == expected_components:
                return full_array

        return data

    def _sync_to_blender(self):
        """Sync the current array data back to the Blender object."""
        if self._blender_object is None:
            return

        # Always sync using the root array to ensure full shape
        root = getattr(self, "_root", self)
        data_to_sync = np.asarray(root).view(np.ndarray)
        data_to_sync = self._ensure_correct_shape(data_to_sync)

        # Ensure float32 dtype
        if data_to_sync.dtype != np.float32:
            data_to_sync = data_to_sync.astype(np.float32)

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

        # Get array representation
        array_repr = np.array_repr(np.asarray(self).view(np.ndarray))

        return (
            f"AttributeArray(name='{attr_name}', object='{obj_name}', mesh='{obj_type}', "
            f"domain={domain_name}, type={atype.value}, shape={self.shape}, dtype={self.dtype})\n"
            f"{array_repr}"
        )
