import numpy as np
import unittest
import pytest
import databpy as db
from databpy.object import AttributeArray, create_bob

np.random.seed(11)


class TestAttributeArray(unittest.TestCase):
    """Test the AttributeArray numpy subclass functionality."""

    def setup_method(self, method=None):
        """Set up test fixtures before each test method."""
        # Create test vertices
        self.test_vertices = np.array(
            [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [1.0, 1.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.5, 0.5, 1.0],
            ]
        )
        self.bob = create_bob(vertices=self.test_vertices, name="TestPositionArray")

    def test_position_array_creation(self):
        """Test that PositionArray is created correctly."""
        pos = self.bob.position

        assert isinstance(pos, AttributeArray)
        assert isinstance(pos, np.ndarray)
        assert pos.shape == (5, 3)
        np.testing.assert_array_equal(pos, self.test_vertices)

    def test_position_array_has_blender_reference(self):
        """Test that PositionArray maintains reference to BlenderObject."""
        pos = self.bob.position

        assert hasattr(pos, "_blender_object")
        assert pos._blender_object is self.bob.object

    def test_numpy_array_properties(self):
        """Test that PositionArray inherits numpy array properties."""
        pos = self.bob.position

        assert pos.shape == (5, 3)
        assert pos.dtype == np.float32 or pos.dtype == np.float64
        assert pos.ndim == 2
        assert len(pos) == 5

    def test_numpy_array_methods(self):
        """Test that PositionArray supports numpy array methods."""
        pos = self.bob.position

        # Test read-only operations
        mean_pos = pos.mean(axis=0)
        assert mean_pos.shape == (3,)

        max_pos = pos.max(axis=0)
        assert max_pos.shape == (3,)

        # Test slicing returns PositionArray or regular array as appropriate
        slice_pos = pos[:3]
        assert isinstance(slice_pos, np.ndarray)

    def test_indexed_assignment(self):
        """Test that indexed assignment works and syncs to Blender."""
        pos = self.bob.position
        pos[0, 2]

        # Modify a single element
        pos[0, 2] = 5.0

        # Check that the change is reflected in the array
        assert pos[0, 2] == 5.0

        # Check that it synced back to Blender
        updated_pos = self.bob.named_attribute("position")
        assert updated_pos[0, 2] == 5.0

    def test_slice_assignment(self):
        """Test that slice assignment works and syncs to Blender."""
        pos = self.bob.position

        # Modify a column (all Z coordinates)
        pos[:, 2] = 2.0

        # Check that all Z coordinates are updated
        np.testing.assert_array_equal(pos[:, 2], [2.0, 2.0, 2.0, 2.0, 2.0])

        # Check that it synced back to Blender
        updated_pos = self.bob.named_attribute("position")
        np.testing.assert_array_equal(updated_pos[:, 2], [2.0, 2.0, 2.0, 2.0, 2.0])

    def test_inplace_addition(self):
        """Test that in-place addition works and syncs to Blender."""
        pos = self.bob.position
        original_pos = pos.copy()

        # Add 1 to all Z coordinates
        pos[:, 2] += 1.0

        # Check the change
        expected = original_pos.copy()
        expected[:, 2] += 1.0
        np.testing.assert_array_almost_equal(pos, expected)

        # Check sync to Blender
        updated_pos = self.bob.named_attribute("position")
        np.testing.assert_array_almost_equal(updated_pos, expected)

    def test_inplace_subtraction(self):
        """Test that in-place subtraction works and syncs to Blender."""
        pos = self.bob.position
        original_pos = pos.copy()

        pos[:, 1] -= 0.5

        expected = original_pos.copy()
        expected[:, 1] -= 0.5
        np.testing.assert_array_almost_equal(pos, expected)

        # Check sync to Blender
        updated_pos = self.bob.named_attribute("position")
        np.testing.assert_array_almost_equal(updated_pos, expected)

    def test_inplace_multiplication(self):
        """Test that in-place multiplication works and syncs to Blender."""
        pos = self.bob.position
        original_pos = pos.copy()

        pos *= 2.0

        expected = original_pos * 2.0
        np.testing.assert_array_almost_equal(pos, expected)

        # Check sync to Blender
        updated_pos = self.bob.named_attribute("position")
        np.testing.assert_array_almost_equal(updated_pos, expected)

    def test_inplace_division(self):
        """Test that in-place division works and syncs to Blender."""
        pos = self.bob.position
        # Set to non-zero values to avoid division issues
        pos[:] = [
            [2.0, 4.0, 6.0],
            [8.0, 10.0, 12.0],
            [14.0, 16.0, 18.0],
            [20.0, 22.0, 24.0],
            [26.0, 28.0, 30.0],
        ]
        original_pos = pos.copy()

        pos /= 2.0

        expected = original_pos / 2.0
        np.testing.assert_array_almost_equal(pos, expected)

        # Check sync to Blender
        updated_pos = self.bob.named_attribute("position")
        np.testing.assert_array_almost_equal(updated_pos, expected)

    def test_complex_indexing_operations(self):
        """Test complex indexing operations like the original use case."""
        pos = self.bob.position

        # The original problematic operation
        pos[:, 2] += 1

        # Check that all Z coordinates increased by 1
        expected_z = self.test_vertices[:, 2] + 1
        np.testing.assert_array_almost_equal(pos[:, 2], expected_z)

        # Check sync to Blender
        updated_pos = self.bob.named_attribute("position")
        np.testing.assert_array_almost_equal(updated_pos[:, 2], expected_z)

    def test_multiple_operations(self):
        """Test multiple consecutive operations."""
        pos = self.bob.position

        # Chain multiple operations
        pos[:, 0] += 1.0
        pos[:, 1] *= 2.0
        pos[0, 2] = 10.0

        # Check final state
        expected = self.test_vertices.copy()
        expected[:, 0] += 1.0
        expected[:, 1] *= 2.0
        expected[0, 2] = 10.0

        np.testing.assert_array_almost_equal(pos, expected)

        # Check sync to Blender
        updated_pos = self.bob.named_attribute("position")
        np.testing.assert_array_almost_equal(updated_pos, expected)

    def test_position_setter_still_works(self):
        """Test that the position setter still works with regular arrays."""
        new_positions = np.array(
            [
                [10.0, 10.0, 10.0],
                [20.0, 20.0, 20.0],
                [30.0, 30.0, 30.0],
                [40.0, 40.0, 40.0],
                [50.0, 50.0, 50.0],
            ]
        )

        # Set using the setter
        self.bob.position = new_positions

        # Check that it worked
        pos = self.bob.position
        np.testing.assert_array_equal(pos, new_positions)

        # Check that it's still a PositionArray
        assert isinstance(pos, AttributeArray)

    def test_array_finalize_preserves_reference(self):
        """Test that array operations preserve the Blender object reference."""
        pos = self.bob.position

        # Operations that might trigger __array_finalize__
        pos[:3]

        # The slice might not be a PositionArray, but the original should still work
        pos[0, 0] = 999.0

        # Check that the reference is still intact
        assert hasattr(pos, "_blender_object")
        assert pos._blender_object is self.bob.object

        # Check that the change synced
        updated_pos = self.bob.named_attribute("position")
        assert updated_pos[0, 0] == 999.0

    def test_column_accessor_array_operations(self):
        """Test that ColumnAccessor supports array operations and wrapping."""
        pos = self.bob.position

        # Set initial test values
        initial_values = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        pos[:, 2] = initial_values

        # Get column accessor for z coordinates
        z_column = pos[:, 2]

        # Test basic array operations that are known to work
        z_column += 2.0

        # Check that the operation applied correctly
        expected = initial_values + 2.0
        np.testing.assert_array_almost_equal(z_column.column_data, expected)

        # Check that it synced back to Blender
        updated_pos = self.bob.named_attribute("position")
        np.testing.assert_array_almost_equal(updated_pos[:, 2], expected)

        # Test another operation
        z_column *= 3.0

        # Check the new result
        expected = (initial_values + 2.0) * 3.0
        np.testing.assert_array_almost_equal(z_column.column_data, expected)

        # Verify sync again
        updated_pos = self.bob.named_attribute("position")
        np.testing.assert_array_almost_equal(updated_pos[:, 2], expected)

    def test_column_accessor_attribute_delegation(self):
        """Test that ColumnAccessor delegates attribute access to the column data."""
        pos = self.bob.position

        # Set initial values
        pos[:, 1] = np.array([1.0, 2.0, 3.0, 4.0, 5.0])

        # Get column accessor
        y_column = pos[:, 1]

        # Test attribute delegation
        assert y_column.mean() == 3.0
        assert y_column.sum() == 15.0
        assert y_column.max() == 5.0
        assert y_column.min() == 1.0

        # Test attribute error for non-existent attribute
        try:
            y_column.nonexistent_attribute
            assert False, "Should have raised AttributeError"
        except AttributeError:
            pass

    def test_column_accessor_array_conversion(self):
        """Test that ColumnAccessor correctly converts to array with optional dtype."""
        pos = self.bob.position

        # Set test values
        pos[:, 0] = np.array([1.0, 2.0, 3.0, 4.0, 5.0])

        # Get column accessor
        x_column = pos[:, 0]

        # Convert to array with default dtype
        arr1 = np.asarray(x_column)
        np.testing.assert_array_equal(arr1, [1.0, 2.0, 3.0, 4.0, 5.0])
        assert arr1.dtype == pos.dtype

        # Convert to array with specified dtype
        arr2 = np.asarray(x_column, dtype=np.int32)
        np.testing.assert_array_equal(arr2, [1, 2, 3, 4, 5])
        assert arr2.dtype == np.int32

        # Test equality comparison
        assert x_column == np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        assert x_column != np.array([5.0, 4.0, 3.0, 2.0, 1.0])

    def test_float_color_attribute_handling(self):
        """Test handling of FLOAT_COLOR attributes (4 components)."""
        from databpy.attribute import AttributeTypes

        # Create a color attribute (RGBA)
        color_data = np.random.rand(5, 4).astype(np.float32)
        self.bob.store_named_attribute(
            color_data, name="color", atype=AttributeTypes.FLOAT_COLOR, domain="POINT"
        )

        # Get as AttributeArray
        colors = AttributeArray(self.bob.object, "color")

        # Verify shape and components
        assert colors.shape == (5, 4)
        assert colors._get_expected_components() == 4

        # Modify and verify sync
        colors[:, 3] = 0.5  # Set alpha to 0.5

        updated_colors = self.bob.named_attribute("color")
        np.testing.assert_array_almost_equal(
            updated_colors[:, 3], [0.5, 0.5, 0.5, 0.5, 0.5]
        )

    def test_equality_comparison(self):
        """Test equality comparisons with different input types."""
        pos = self.bob.position

        # Set known values
        test_data = np.array(
            [
                [1.0, 2.0, 3.0],
                [4.0, 5.0, 6.0],
                [7.0, 8.0, 9.0],
                [10.0, 11.0, 12.0],
                [13.0, 14.0, 15.0],
            ]
        )
        pos[:] = test_data

        # Compare with numpy array using __eq__ method
        assert pos == test_data

        # For inequality, use np.array_equal with a not operator
        modified_data = test_data + 1.0
        assert not np.array_equal(np.asarray(pos), modified_data)

        # Compare with a column
        column_data = np.array([1.0, 4.0, 7.0, 10.0, 13.0])
        assert pos[:, 0] == column_data

        # Compare with another AttributeArray
        other_bob = create_bob(vertices=test_data, name="OtherTest")
        other_pos = other_bob.position
        assert pos == other_pos

        # Test that non-equality works correctly
        other_bob2 = create_bob(vertices=test_data + 2.0, name="DifferentTest")
        different_pos = other_bob2.position
        assert not np.array_equal(np.asarray(pos), np.asarray(different_pos))

        # Test comparison with array of different shape but matching column
        column_data = np.array([3.0, 6.0, 9.0, 12.0, 15.0])
        # This should match the 3rd column (index 2)
        assert np.array_equal(pos[:, 2], column_data)

    def test_column_accessor_array_wrapping_and_ufuncs(self):
        """Test ColumnAccessor handling of numpy ufuncs and array wrapping."""
        pos = self.bob.position

        # Set initial values
        pos[:, 0] = np.array([1.0, 2.0, 3.0, 4.0, 5.0])

        # Get column accessor
        x_column = pos[:, 0]

        # Test standard operations instead of direct ufuncs
        x_column += 10.0

        # Check that operation updated values and synced
        np.testing.assert_array_equal(pos[:, 0], [11.0, 12.0, 13.0, 14.0, 15.0])
        updated_pos = self.bob.named_attribute("position")
        np.testing.assert_array_almost_equal(
            updated_pos[:, 0], [11.0, 12.0, 13.0, 14.0, 15.0]
        )

        # Save current values
        original = np.array(pos[:, 0])

        # Apply sqrt using standard assignment
        pos[:, 0] = np.sqrt(pos[:, 0])

        # Check results
        expected = np.sqrt(original)
        np.testing.assert_array_almost_equal(pos[:, 0], expected)
        updated_pos = self.bob.named_attribute("position")
        np.testing.assert_array_almost_equal(updated_pos[:, 0], expected)

        # Square the values to get back to original (approximately)
        pos[:, 0] = np.square(pos[:, 0])
        np.testing.assert_array_almost_equal(pos[:, 0], original)

    def test_error_handling_for_invalid_operations(self):
        """Test error handling for invalid operations on AttributeArray and ColumnAccessor."""
        pos = self.bob.position

        # Test incompatible shape for assignment
        with pytest.raises(ValueError):
            pos[:] = np.random.rand(10, 5)  # Wrong number of columns

        # Test incompatible shape for column assignment
        with pytest.raises(ValueError):
            pos[:, 0] = np.random.rand(10)  # Wrong number of rows

        # Test invalid column index
        with pytest.raises(IndexError):
            pos[:, 5] = 1.0  # Column index out of bounds

        # Test invalid item assignment
        with pytest.raises(IndexError):
            pos[10, 0] = 1.0  # Row index out of bounds

        # Test invalid operation on column accessor
        column = pos[:, 0]
        # Use pytest for all assertions for consistency
        with pytest.raises((TypeError, ValueError)):
            column + "string"  # Incompatible type for operation

    def test_mixed_type_operations(self):
        """Test operations with mixed data types on AttributeArray and ColumnAccessor."""
        pos = self.bob.position

        # Initialize with float values
        pos[:] = np.ones((5, 3), dtype=np.float32)

        # Test mixed-type addition (integer)
        pos[:, 0] += 1
        np.testing.assert_array_equal(pos[:, 0], [2.0, 2.0, 2.0, 2.0, 2.0])

        # Test mixed-type multiplication (integer)
        pos[:, 1] *= 2
        np.testing.assert_array_equal(pos[:, 1], [2.0, 2.0, 2.0, 2.0, 2.0])

        # Test with boolean array
        mask = np.array([True, False, True, False, True])
        pos[mask, 2] = 3.0
        expected = np.array([3.0, 1.0, 3.0, 1.0, 3.0])
        np.testing.assert_array_equal(pos[:, 2], expected)

        # Test operations with numpy int64/float64 scalars
        pos[:, 0] += np.int64(3)
        np.testing.assert_array_equal(pos[:, 0], [5.0, 5.0, 5.0, 5.0, 5.0])

        pos[:, 1] *= np.float64(1.5)
        np.testing.assert_array_equal(pos[:, 1], [3.0, 3.0, 3.0, 3.0, 3.0])

        # Check sync to Blender
        updated_pos = self.bob.named_attribute("position")
        np.testing.assert_array_almost_equal(updated_pos, pos)

    def test_multiple_column_operations(self):
        """Test operations on multiple columns simultaneously."""
        pos = self.bob.position

        # Initialize with known values
        pos[:] = np.ones((5, 3), dtype=np.float32)

        # Test modifying multiple columns in a single operation
        pos[:, [0, 2]] = np.array(
            [[2.0, 3.0], [2.0, 3.0], [2.0, 3.0], [2.0, 3.0], [2.0, 3.0]]
        )

        # Check results
        np.testing.assert_array_equal(pos[:, 0], [2.0, 2.0, 2.0, 2.0, 2.0])
        np.testing.assert_array_equal(pos[:, 1], [1.0, 1.0, 1.0, 1.0, 1.0])
        np.testing.assert_array_equal(pos[:, 2], [3.0, 3.0, 3.0, 3.0, 3.0])

        # Test boolean indexing for multiple columns
        mask = np.array([True, False, True, False, True])
        pos[mask, :] = np.array([[5.0, 5.0, 5.0], [6.0, 6.0, 6.0], [7.0, 7.0, 7.0]])

        # Check results
        expected = np.array(
            [
                [5.0, 5.0, 5.0],
                [2.0, 1.0, 3.0],
                [6.0, 6.0, 6.0],
                [2.0, 1.0, 3.0],
                [7.0, 7.0, 7.0],
            ]
        )
        np.testing.assert_array_equal(pos, expected)

        # Check sync to Blender
        updated_pos = self.bob.named_attribute("position")
        np.testing.assert_array_almost_equal(updated_pos, expected)

        # Test range slicing
        pos[1:4, 0:2] = 9.0
        expected[1:4, 0:2] = 9.0
        np.testing.assert_array_equal(pos, expected)

        # Check sync to Blender
        updated_pos = self.bob.named_attribute("position")
        np.testing.assert_array_almost_equal(updated_pos, expected)


def test_position_array_integration():
    """Integration test with the broader databpy ecosystem."""
    # Create object using create_bob
    vertices = np.random.rand(10, 3)
    bob = create_bob(vertices=vertices, name="IntegrationTest")

    # Test that position returns PositionArray
    pos = bob.position
    assert isinstance(pos, AttributeArray)

    # Test the original use case that was broken
    pos[:, 2] += 1.0

    # Verify the change
    expected_z = vertices[:, 2] + 1.0
    np.testing.assert_array_almost_equal(pos[:, 2], expected_z)

    # Test with ObjectTracker context manager
    from databpy.object import ObjectTracker

    with ObjectTracker() as tracker:
        create_bob(vertices=np.random.rand(5, 3), name="TrackedObject")

    tracked_objects = tracker.new_objects()
    assert len(tracked_objects) == 1

    # Test position array on tracked object
    tracked_bob = db.BlenderObject(tracked_objects[0])
    tracked_pos = tracked_bob.position
    assert isinstance(tracked_pos, AttributeArray)

    # Test modification
    tracked_pos += 0.5
    updated = tracked_bob.named_attribute("position")
    assert np.all(updated >= 0.5)
