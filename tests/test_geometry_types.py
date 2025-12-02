"""Tests for Curves and PointCloud object creation and manipulation."""

import numpy as np
import pytest
import bpy
import databpy as db


class TestMeshCreation:
    """Tests for mesh object creation with new API."""

    def test_create_mesh_object(self):
        """Test create_mesh_object() creates a valid mesh."""
        vertices = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]])
        faces = [(0, 1, 2, 3)]
        obj = db.create_mesh_object(vertices, faces=faces, name="TestMesh")

        assert isinstance(obj.data, bpy.types.Mesh)
        assert len(obj.data.vertices) == 4
        assert obj.name == "TestMesh"

    def test_create_mesh_bob(self):
        """Test create_mesh_bob() creates a valid BlenderObject."""
        vertices = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0]])
        bob = db.BlenderObject.from_mesh(vertices, name="TestMeshBob")

        assert isinstance(bob, db.BlenderObject)
        assert isinstance(bob.data, bpy.types.Mesh)
        assert len(bob) == 3
        assert bob.name == "TestMeshBob"

    def test_create_mesh_empty(self):
        """Test creating an empty mesh."""
        obj = db.create_mesh_object(name="EmptyMesh")

        assert isinstance(obj.data, bpy.types.Mesh)
        assert len(obj.data.vertices) == 0

    def test_create_mesh_with_edges(self):
        """Test creating a mesh with edges."""
        vertices = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0]])
        edges = [(0, 1), (1, 2)]
        obj = db.create_mesh_object(vertices, edges=edges, name="EdgeMesh")

        assert len(obj.data.vertices) == 3
        assert len(obj.data.edges) == 2


class TestCurvesCreation:
    """Tests for curves object creation."""

    def test_create_curves_object(self):
        """Test create_curves_object() creates valid curves."""
        positions = np.random.random((10, 3)).astype(np.float32)
        curve_sizes = [3, 4, 3]
        obj = db.create_curves_object(positions, curve_sizes, name="TestCurves")

        assert isinstance(obj.data, bpy.types.Curves)
        assert len(obj.data.curves) == 3
        assert len(obj.data.points) == 10
        assert obj.name == "TestCurves"

    def test_create_curves_bob(self):
        """Test create_curves_bob() creates a valid BlenderObject."""
        positions = np.random.random((7, 3)).astype(np.float32)
        curve_sizes = [3, 4]
        bob = db.BlenderObject.from_curves(positions, curve_sizes, name="TestCurvesBob")

        assert isinstance(bob, db.BlenderObject)
        assert isinstance(bob.data, bpy.types.Curves)
        assert len(bob) == 7
        assert bob.name == "TestCurvesBob"

    def test_create_curves_positions_preserved(self):
        """Test that positions are correctly stored in curves."""
        test_positions = np.array(
            [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]], dtype=np.float32
        )
        curve_sizes = [3]
        bob = db.BlenderObject.from_curves(test_positions, curve_sizes, name="TestPos")

        retrieved_positions = bob.named_attribute("position")
        assert np.allclose(test_positions, retrieved_positions, atol=1e-6)

    def test_create_curves_empty(self):
        """Test creating an empty curves object."""
        obj = db.create_curves_object(name="EmptyCurves")

        assert isinstance(obj.data, bpy.types.Curves)
        assert len(obj.data.curves) == 0
        assert len(obj.data.points) == 0

    def test_create_curves_multiple_curves(self):
        """Test creating multiple curves with different sizes."""
        positions = np.random.random((15, 3)).astype(np.float32)
        curve_sizes = [2, 5, 3, 5]  # 4 curves with different point counts
        obj = db.create_curves_object(positions, curve_sizes, name="MultiCurves")

        assert len(obj.data.curves) == 4
        assert len(obj.data.points) == 15

    def test_create_curves_size_mismatch_error(self):
        """Test that mismatched positions and curve_sizes raises ValueError."""
        positions = np.random.random((10, 3)).astype(np.float32)
        curve_sizes = [3, 4, 2]  # Sum is 9, not 10

        with pytest.raises(ValueError, match="Total points in curve_sizes"):
            db.create_curves_object(positions, curve_sizes)


class TestPointCloudCreation:
    """Tests for point cloud object creation."""

    def test_create_pointcloud_object(self):
        """Test create_pointcloud_object() creates valid point cloud."""
        positions = np.random.random((50, 3)).astype(np.float32)
        obj = db.create_pointcloud_object(positions, name="TestPC")

        assert isinstance(obj.data, bpy.types.PointCloud)
        assert len(obj.data.points) == 50
        assert obj.name == "TestPC"

    def test_create_pointcloud_bob(self):
        """Test create_pointcloud_bob() creates a valid BlenderObject."""
        positions = np.random.random((100, 3)).astype(np.float32)
        bob = db.BlenderObject.from_pointcloud(positions, name="TestPCBob")

        assert isinstance(bob, db.BlenderObject)
        assert isinstance(bob.data, bpy.types.PointCloud)
        assert len(bob) == 100
        assert bob.name == "TestPCBob"

    def test_create_pointcloud_positions_preserved(self):
        """Test that positions are correctly stored in point cloud."""
        test_positions = np.array(
            [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]],
            dtype=np.float32,
        )
        bob = db.BlenderObject.from_pointcloud(test_positions, name="TestPCPos")

        retrieved_positions = bob.named_attribute("position")
        assert np.allclose(test_positions, retrieved_positions, atol=1e-6)

    def test_create_pointcloud_empty(self):
        """Test creating an empty point cloud."""
        obj = db.create_pointcloud_object(name="EmptyPC")

        assert isinstance(obj.data, bpy.types.PointCloud)
        assert len(obj.data.points) == 0

    def test_create_pointcloud_large(self):
        """Test creating a large point cloud."""
        positions = np.random.random((1000, 3)).astype(np.float32)
        obj = db.create_pointcloud_object(positions, name="LargePC")

        assert len(obj.data.points) == 1000


class TestBlenderObjectLen:
    """Tests for __len__ method across all geometry types."""

    def test_len_mesh(self):
        """Test __len__ returns vertex count for mesh objects."""
        vertices = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]])
        bob = db.BlenderObject.from_mesh(vertices)

        assert len(bob) == 4
        assert len(bob) == len(bob.data.vertices)

    def test_len_curves(self):
        """Test __len__ returns point count for curves objects."""
        positions = np.random.random((12, 3)).astype(np.float32)
        curve_sizes = [4, 5, 3]
        bob = db.BlenderObject.from_curves(positions, curve_sizes)

        assert len(bob) == 12
        assert len(bob) == len(bob.data.points)

    def test_len_pointcloud(self):
        """Test __len__ returns point count for point cloud objects."""
        positions = np.random.random((75, 3)).astype(np.float32)
        bob = db.BlenderObject.from_pointcloud(positions)

        assert len(bob) == 75
        assert len(bob) == len(bob.data.points)

    def test_len_empty_objects(self):
        """Test __len__ returns 0 for empty objects."""
        mesh_bob = db.BlenderObject.from_mesh()
        curves_bob = db.BlenderObject.from_curves()
        pc_bob = db.BlenderObject.from_pointcloud()

        assert len(mesh_bob) == 0
        assert len(curves_bob) == 0
        assert len(pc_bob) == 0

    def test_len_old_curve_type_raises_error(self):
        """Test __len__ raises TypeError for unsupported old Curve type."""
        # Create old Curve type
        bpy.ops.curve.primitive_bezier_curve_add()
        old_curve_obj = bpy.context.active_object
        bob = db.BlenderObject(old_curve_obj)

        with pytest.raises(TypeError, match="not supported"):
            len(bob)


class TestAttributeAccess:
    """Tests for attribute access across geometry types."""

    def test_mesh_attribute_access(self):
        """Test attribute access on mesh objects."""
        vertices = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0]])
        bob = db.BlenderObject.from_mesh(vertices)

        positions = bob.named_attribute("position")
        assert positions.shape == (3, 3)
        assert np.allclose(positions, vertices)

    def test_curves_attribute_access(self):
        """Test attribute access on curves objects."""
        positions = np.random.random((5, 3)).astype(np.float32)
        curve_sizes = [5]
        bob = db.BlenderObject.from_curves(positions, curve_sizes)

        retrieved = bob.named_attribute("position")
        assert retrieved.shape == (5, 3)
        assert np.allclose(positions, retrieved, atol=1e-6)

    def test_pointcloud_attribute_access(self):
        """Test attribute access on point cloud objects."""
        positions = np.random.random((20, 3)).astype(np.float32)
        bob = db.BlenderObject.from_pointcloud(positions)

        retrieved = bob.named_attribute("position")
        assert retrieved.shape == (20, 3)
        assert np.allclose(positions, retrieved, atol=1e-6)

    def test_mesh_getitem_syntax(self):
        """Test dictionary-style attribute access on mesh."""
        vertices = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0]])
        bob = db.BlenderObject.from_mesh(vertices)

        positions = bob["position"]
        assert isinstance(positions, db.AttributeArray)
        assert positions.shape == (3, 3)

    def test_curves_getitem_syntax(self):
        """Test dictionary-style attribute access on curves."""
        positions = np.random.random((8, 3)).astype(np.float32)
        curve_sizes = [3, 5]
        bob = db.BlenderObject.from_curves(positions, curve_sizes)

        retrieved = bob["position"]
        assert isinstance(retrieved, db.AttributeArray)
        assert retrieved.shape == (8, 3)

    def test_pointcloud_getitem_syntax(self):
        """Test dictionary-style attribute access on point cloud."""
        positions = np.random.random((30, 3)).astype(np.float32)
        bob = db.BlenderObject.from_pointcloud(positions)

        retrieved = bob["position"]
        assert isinstance(retrieved, db.AttributeArray)
        assert retrieved.shape == (30, 3)


class TestDeprecationWarnings:
    """Tests for deprecation warnings on old API."""

    def test_vertices_property_deprecation(self):
        """Test BlenderObject.vertices shows deprecation warning."""
        bob = db.BlenderObject.from_mesh([[0, 0, 0], [1, 0, 0]])

        with pytest.warns(DeprecationWarning, match="vertices is deprecated"):
            vertices = bob.vertices

        assert len(vertices) == 2

    def test_edges_property_deprecation(self):
        """Test BlenderObject.edges shows deprecation warning."""
        bob = db.BlenderObject.from_mesh([[0, 0, 0], [1, 0, 0]])

        with pytest.warns(DeprecationWarning, match="edges is deprecated"):
            edges = bob.edges

        # Edges might be empty but property should work
        assert hasattr(edges, "__len__")

    def test_vertices_on_non_mesh_raises_error(self):
        """Test vertices property raises error on non-mesh objects."""
        bob = db.BlenderObject.from_curves(
            np.random.random((5, 3)).astype(np.float32), [5]
        )

        with pytest.warns(DeprecationWarning):
            with pytest.raises(AttributeError, match="only works with Mesh"):
                _ = bob.vertices

    def test_edges_on_non_mesh_raises_error(self):
        """Test edges property raises error on non-mesh objects."""
        bob = db.BlenderObject.from_pointcloud(
            np.random.random((10, 3)).astype(np.float32)
        )

        with pytest.warns(DeprecationWarning):
            with pytest.raises(AttributeError, match="only works with Mesh"):
                _ = bob.edges


class TestCollectionHandling:
    """Tests for collection assignment in creation functions."""

    def test_mesh_in_custom_collection(self):
        """Test creating mesh in custom collection."""
        col = db.create_collection("TestCollection")
        obj = db.create_mesh_object([[0, 0, 0]], collection=col)

        assert obj.name in col.objects

    def test_curves_in_custom_collection(self):
        """Test creating curves in custom collection."""
        col = db.create_collection("CurvesCollection")
        obj = db.create_curves_object(
            np.random.random((3, 3)).astype(np.float32), [3], collection=col
        )

        assert obj.name in col.objects

    def test_pointcloud_in_custom_collection(self):
        """Test creating point cloud in custom collection."""
        col = db.create_collection("PCCollection")
        obj = db.create_pointcloud_object(
            np.random.random((5, 3)).astype(np.float32), collection=col
        )

        assert obj.name in col.objects


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_curves_with_single_curve(self):
        """Test creating curves with a single curve."""
        positions = np.random.random((10, 3)).astype(np.float32)
        obj = db.create_curves_object(positions, [10])

        assert len(obj.data.curves) == 1
        assert len(obj.data.points) == 10

    def test_curves_with_single_point_curves(self):
        """Test creating multiple curves each with single point."""
        positions = np.random.random((5, 3)).astype(np.float32)
        obj = db.create_curves_object(positions, [1, 1, 1, 1, 1])

        assert len(obj.data.curves) == 5
        assert len(obj.data.points) == 5

    def test_pointcloud_with_single_point(self):
        """Test creating point cloud with a single point."""
        positions = np.array([[1.0, 2.0, 3.0]], dtype=np.float32)
        obj = db.create_pointcloud_object(positions)

        assert len(obj.data.points) == 1

    def test_mesh_with_2d_positions_converts_to_3d(self):
        """Test that 2D positions raise an error."""
        # Blender requires 3D coordinates, 2D should fail
        vertices = [[0, 0], [1, 0]]
        with pytest.raises(RuntimeError, match="internal error setting the array"):
            db.create_mesh_object(vertices)

    def test_pointcloud_from_list_input(self):
        """Test creating point cloud from list instead of numpy array."""
        positions = [[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]]
        obj = db.create_pointcloud_object(positions)

        assert len(obj.data.points) == 2

    def test_curves_from_list_input(self):
        """Test creating curves from list instead of numpy array."""
        positions = [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0]]
        curve_sizes = [3]
        obj = db.create_curves_object(positions, curve_sizes)

        assert len(obj.data.points) == 3
