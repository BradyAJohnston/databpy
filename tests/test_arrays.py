import numpy as np
import pytest
import databpy as db
from databpy.object import AttributeArray, BlenderObject, create_bob
from databpy.attribute import AttributeTypes, AttributeDomains

np.random.seed(11)


class TestAttributeArray:
    """Test the AttributeArray numpy subclass functionality."""

    def setup_method(self):
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
        assert pos._blender_object is self.bob

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
        original_z = pos[0, 2]

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
        sliced = pos[:3]

        # The slice might not be a PositionArray, but the original should still work
        pos[0, 0] = 999.0

        # Check that the reference is still intact
        assert hasattr(pos, "_blender_object")
        assert pos._blender_object is self.bob

        # Check that the change synced
        updated_pos = self.bob.named_attribute("position")
        assert updated_pos[0, 0] == 999.0


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
        new_bob = create_bob(vertices=np.random.rand(5, 3), name="TrackedObject")

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
