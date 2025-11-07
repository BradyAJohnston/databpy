"""Tests for BlenderObjectBase class methods."""

import pytest
import numpy as np
import bpy
import databpy as db


class TestBlenderObjectBase:
    """Test core BlenderObjectBase functionality."""

    def test_setitem_syntax_new_attribute(self):
        """Test setting a new attribute using dictionary-style syntax."""
        vertices = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0]])
        bob = db.BlenderObject.from_mesh(vertices)

        # Set a new custom attribute
        custom_data = np.array([1.0, 2.0, 3.0])
        bob["custom_attr"] = custom_data

        # Verify it was stored
        retrieved = bob.named_attribute("custom_attr")
        assert np.allclose(retrieved, custom_data)

    def test_setitem_syntax_existing_attribute(self):
        """Test updating an existing attribute using dictionary-style syntax."""
        vertices = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0]])
        bob = db.BlenderObject.from_mesh(vertices)

        # Store initial attribute
        initial_data = np.array([1.0, 2.0, 3.0])
        bob.store_named_attribute(initial_data, "test_attr")

        # Update using setitem
        new_data = np.array([4.0, 5.0, 6.0])
        bob["test_attr"] = new_data

        # Verify it was updated
        retrieved = bob.named_attribute("test_attr")
        assert np.allclose(retrieved, new_data)
        assert not np.allclose(retrieved, initial_data)

    def test_data_property_mesh(self):
        """Test data property returns correct data block for mesh."""
        vertices = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0]])
        bob = db.BlenderObject.from_mesh(vertices)

        # Access data property
        data = bob.data
        assert isinstance(data, bpy.types.Mesh)
        assert len(data.vertices) == 3

    def test_data_property_curves(self):
        """Test data property returns correct data block for curves."""
        positions = np.random.random((5, 3)).astype(np.float32)
        curve_sizes = [5]
        bob = db.BlenderObject.from_curves(positions, curve_sizes)

        # Access data property
        data = bob.data
        assert isinstance(data, bpy.types.Curves)

    def test_data_property_pointcloud(self):
        """Test data property returns correct data block for point cloud."""
        positions = np.random.random((10, 3)).astype(np.float32)
        bob = db.BlenderObject.from_pointcloud(positions)

        # Access data property
        data = bob.data
        assert isinstance(data, bpy.types.PointCloud)
        assert len(data.points) == 10

    def test_attributes_property(self):
        """Test attributes property returns attributes collection."""
        vertices = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0]])
        bob = db.BlenderObject.from_mesh(vertices)

        # Access attributes property
        attrs = bob.attributes
        # Verify it's an attributes collection by checking interface
        assert hasattr(attrs, "__getitem__")
        assert "position" in attrs

    def test_attributes_property_with_custom_attributes(self):
        """Test attributes property includes custom attributes."""
        vertices = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0]])
        bob = db.BlenderObject.from_mesh(vertices)

        # Add custom attribute
        custom_data = np.array([1.0, 2.0, 3.0])
        bob.store_named_attribute(custom_data, "custom_attr")

        # Verify it's in attributes collection
        attrs = bob.attributes
        assert "custom_attr" in attrs
        assert attrs["custom_attr"] is not None

    def test_evaluate_method(self):
        """Test evaluate method returns evaluated object."""
        vertices = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0]])
        bob = db.BlenderObject.from_mesh(vertices)

        # Call evaluate
        evaluated_obj = bob.evaluate()
        assert isinstance(evaluated_obj, bpy.types.Object)
        assert evaluated_obj.data is not None
