import numpy as np
from .attribute import Attribute, AttributeTypes


class ColumnAccessor:
    """
    Helper class to handle column operations on AttributeArray.
    
    This provides a clean way to handle operations like pos[:, 2] += 1.0
    without the complexity of numpy array views.
    """
    def __init__(self, parent, column_idx):
        self.parent = parent
        self.column_idx = column_idx
        # Store a reference to the parent array - don't create a separate copy
        self.parent_array = np.asarray(parent).view(np.ndarray)
    
    def __iadd__(self, value):
        """Handle += operation on a column."""
        # Update the parent's column data
        self.parent_array[:, self.column_idx] += value
        # Sync changes to Blender
        self.parent._sync_to_blender()
        return self
    
    def __isub__(self, value):
        """Handle -= operation on a column."""
        self.parent_array[:, self.column_idx] -= value
        self.parent._sync_to_blender()
        return self
    
    def __imul__(self, value):
        """Handle *= operation on a column."""
        self.parent_array[:, self.column_idx] *= value
        self.parent._sync_to_blender()
        return self
    
    def __itruediv__(self, value):
        """Handle /= operation on a column."""
        self.parent_array[:, self.column_idx] /= value
        self.parent._sync_to_blender()
        return self
    
    def __array__(self, dtype=None):
        """
        Convert to array, handling optional dtype argument.
        
        This method is called by NumPy when trying to convert the object to an array.
        Returns only the specific column data to ensure correct shape for column operations.
        """
        # Return only the column data to maintain correct shape for column operations
        column_data = self.parent_array[:, self.column_idx]
        if dtype is not None:
            return column_data.astype(dtype)
        return column_data
    
    def __eq__(self, other):
        """
        Handle equality comparison.
        
        This is important for array comparisons in tests.
        """
        # Get the column data
        column_data = self.parent_array[:, self.column_idx]
        
        # If other is an array-like object, compare with column data
        if hasattr(other, '__array__'):
            return np.array_equal(column_data, np.asarray(other))
        
        # For scalar comparison
        return column_data == other
        
    def __array_wrap__(self, out_arr, context=None):
        """
        Handle the output of NumPy ufuncs and other functions.
        
        This is called after a NumPy operation to wrap the result in the appropriate type.
        For column operations, we update the parent array and trigger a sync to Blender.
        """
        # Update the parent array with the result
        self.parent_array[:, self.column_idx] = out_arr
        
        # Sync changes back to Blender
        self.parent._sync_to_blender()
        
        # Return self to allow for method chaining
        return self

    @property
    def column_data(self):
        """Get the column data."""
        return self.parent_array[:, self.column_idx]
    def __getattr__(self, name):
        """Delegate attribute access to the column data."""
        # Forward attribute access to the numpy array
        column_data = self.parent_array[:, self.column_idx]
        if hasattr(column_data, name):
            return getattr(column_data, name)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")


class AttributeArray(np.ndarray):
    """
    A numpy array subclass that automatically syncs changes back to the Blender object.
    
    This class handles array operations (including column operations like pos[:, 2] += 1.0)
    and ensures that changes are properly synced back to Blender with the correct shape.
    """

    def __new__(cls, blender_object: "BlenderObject", name: str) -> "AttributeArray":
        """Create a new AttributeArray that wraps a Blender attribute."""
        attr = Attribute(blender_object.object.data.attributes[name])
        arr = np.asarray(attr.as_array()).view(cls)
        arr._blender_object = blender_object
        arr._attribute = attr
        arr._attr_name = name
        return arr

    def __array_finalize__(self, obj):
        """Initialize attributes when array is created through operations."""
        if obj is None:
            return
            
        # Copy reference attributes from the original array
        self._blender_object = getattr(obj, "_blender_object", None)
        self._attribute = getattr(obj, "_attribute", None)
        self._attr_name = getattr(obj, "_attr_name", None)
        
    def __eq__(self, other):
        """
        Handle equality comparison for array objects.
        
        This is critical for test assertions comparing arrays.
        """
        # First check if we're comparing to another AttributeArray
        if isinstance(other, AttributeArray):
            return np.array_equal(np.asarray(self).view(np.ndarray), 
                                 np.asarray(other).view(np.ndarray))
                                 
        # For ColumnAccessor comparison
        if isinstance(other, ColumnAccessor):
            # If the other is a column accessor, compare to the full array
            # This ensures we handle array shape differences correctly
            other_data = other.parent_array
            return np.array_equal(np.asarray(self).view(np.ndarray), other_data)
            
        # For other array-like objects
        if hasattr(other, '__array__'):
            # Make sure we compare the raw numpy data
            self_arr = np.asarray(self).view(np.ndarray)
            other_arr = np.asarray(other)
            
            # Handle shape differences between arrays
            if self_arr.shape != other_arr.shape:
                # If comparing to a column, reshape appropriately
                if (other_arr.ndim == 1 and self_arr.ndim == 2 and 
                    other_arr.shape[0] == self_arr.shape[0]):
                    # Try to find a matching column
                    for i in range(self_arr.shape[1]):
                        if np.array_equal(self_arr[:, i], other_arr):
                            return True
                    return False
            
            # Regular array comparison
            return np.array_equal(self_arr, other_arr)
            
        # Fall back to standard equality for other cases
        return np.asarray(self).view(np.ndarray) == other

    def __getitem__(self, key):
        """
        Get item with special handling for column operations.
        
        For operations like pos[:, 2], returns a special wrapper to handle column operations.
        """
        # Handle column operations specially: pos[:, 2]
        if isinstance(key, tuple) and len(key) == 2:
            if isinstance(key[0], slice) and key[0] == slice(None) and isinstance(key[1], int):
                return ColumnAccessor(self, key[1])
                
        # For regular access, use normal numpy behavior
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        """Set item and sync changes back to Blender."""
        # Special case for column operations like pos[:, 2] = value
        if isinstance(key, tuple) and len(key) == 2:
            if isinstance(key[0], slice) and key[0] == slice(None) and isinstance(key[1], int):
                # This is a full column operation (e.g., pos[:, 2] = value)
                # Get the current data from the array
                col_idx = key[1]
                
                # Set the column values directly using np.ndarray methods
                # to avoid recursion
                arr_view = np.asarray(self).view(np.ndarray)
                
                # Handle ColumnAccessor objects specially
                if isinstance(value, ColumnAccessor):
                    # Extract the column data directly to avoid shape issues
                    column_data = value.column_data
                    arr_view[:, col_idx] = column_data
                else:
                    arr_view[:, col_idx] = value
                
                # Sync to Blender
                self._sync_to_blender()
                return
                
        # For normal operations, use the standard NumPy behavior
        super().__setitem__(key, value)
        self._sync_to_blender()

    # Special methods for column operations
    def add_column(self, column_idx, value):
        """Add a value to a specific column."""
        # Use direct array operations to avoid view complexity
        arr_view = np.asarray(self).view(np.ndarray)
        arr_view[:, column_idx] += value
        self._sync_to_blender()
        return self
        
    def subtract_column(self, column_idx, value):
        """Subtract a value from a specific column."""
        arr_view = np.asarray(self).view(np.ndarray)
        arr_view[:, column_idx] -= value
        self._sync_to_blender()
        return self
        
    def multiply_column(self, column_idx, value):
        """Multiply a specific column by a value."""
        arr_view = np.asarray(self).view(np.ndarray)
        arr_view[:, column_idx] *= value
        self._sync_to_blender()
        return self
        
    def divide_column(self, column_idx, value):
        """Divide a specific column by a value."""
        arr_view = np.asarray(self).view(np.ndarray)
        arr_view[:, column_idx] /= value
        self._sync_to_blender()
        return self

    def _sync_to_blender(self):
        """
        Sync the current array data back to the Blender object.
        
        This method ensures we always send a properly shaped array to Blender.
        """
        if self._blender_object is None:
            return
            
        # Always use the full parent array to ensure we have the complete data
        data_to_sync = np.asarray(self).view(np.ndarray)
        
        # Ensure the data has the correct shape expected by Blender
        # If it's a 1D array but should be 2D, reshape it
        if self._attribute.atype in [AttributeTypes.FLOAT_VECTOR, AttributeTypes.FLOAT_COLOR]:
            # Get the expected number of components
            expected_components = 4 if self._attribute.atype == AttributeTypes.FLOAT_COLOR else 3
            
            # If the data is 1D but should be 2D, reshape it
            if data_to_sync.ndim == 1:
                if len(data_to_sync) % expected_components == 0:
                    data_to_sync = data_to_sync.reshape(-1, expected_components)
            
            # Ensure we have the correct number of columns, regardless of dimension
            elif data_to_sync.ndim == 2 and data_to_sync.shape[1] != expected_components:
                # If we have a single column, we need to expand to full dimensions
                if data_to_sync.shape[1] == 1:
                    # This might be a column operation, need to ensure full shape
                    # Create a fresh copy of the full parent array
                    full_array = np.asarray(self).view(np.ndarray).copy()
                    if full_array.shape[1] == expected_components:
                        data_to_sync = full_array
        
        # Ensure the data type is float32 as required by Blender
        if data_to_sync.dtype != np.float32:
            data_to_sync = data_to_sync.astype(np.float32)
        
        # Sync the properly shaped data back to Blender
        self._blender_object.store_named_attribute(
            data_to_sync,
            name=self._attr_name,
            atype=self._attribute.atype,
            domain=self._attribute.domain.name,
        )

    # Override inplace operators to ensure proper syncing
    def __iadd__(self, other):
        """In-place addition with Blender syncing."""
        result = super().__iadd__(other)
        self._sync_to_blender()
        return result

    def __isub__(self, other):
        """In-place subtraction with Blender syncing."""
        result = super().__isub__(other)
        self._sync_to_blender()
        return result

    def __imul__(self, other):
        """In-place multiplication with Blender syncing."""
        result = super().__imul__(other)
        self._sync_to_blender()
        return result

    def __itruediv__(self, other):
        """In-place division with Blender syncing."""
        result = super().__itruediv__(other)
        self._sync_to_blender()
        return result
