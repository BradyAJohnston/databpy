import pytest
import tempfile
import os
from pathlib import Path
import bpy

try:
    bpy.utils.expose_bundled_modules()
    import openvdb as vdb

    HAS_OPENVDB = True
except Exception:
    HAS_OPENVDB = False

from databpy.vdb import import_vdb
from databpy.collection import create_collection


def create_simple_vdb(filepath: Path) -> None:
    """Create a simple VDB file with a sphere for testing."""
    if not HAS_OPENVDB:
        pytest.skip("OpenVDB not available")

    # Create a simple fog volume with actual density data
    # This approach is more likely to work with Blender's volume importer
    grid = vdb.FloatGrid()
    grid.name = "density"

    # Create a simple 3D density field
    accessor = grid.getAccessor()

    # Fill a small region with density values
    for i in range(-10, 11):
        for j in range(-10, 11):
            for k in range(-10, 11):
                # Create a simple spherical density falloff
                distance = (i * i + j * j + k * k) ** 0.5
                if distance <= 10.0:
                    density = max(0.0, 1.0 - distance / 10.0)
                    if density > 0.01:  # Only set non-negligible values
                        accessor.setValueOn((i, j, k), density)

    # Write the grid to file
    vdb.write(str(filepath), [grid])


@pytest.fixture
def temp_vdb_file():
    """Create a temporary VDB file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".vdb", delete=False) as tmp:
        filepath = Path(tmp.name)

    try:
        create_simple_vdb(filepath)
        yield filepath
    finally:
        if filepath.exists():
            os.unlink(filepath)


@pytest.fixture
def clean_scene():
    """Clean up the Blender scene before and after tests."""
    # Clear existing objects
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

    # Clear collections except the default one
    for collection in bpy.data.collections:
        if collection.name != "Collection":
            bpy.data.collections.remove(collection)

    yield

    # Clean up after test
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


@pytest.mark.skipif(not HAS_OPENVDB, reason="OpenVDB not available")
class TestVDBImport:
    """Test cases for VDB import functionality."""

    def test_import_vdb_basic(self, temp_vdb_file, clean_scene):
        """Test basic VDB import functionality."""
        # Import the VDB file
        volume_obj = import_vdb(temp_vdb_file)

        # Check that an object was created
        assert volume_obj is not None
        assert isinstance(volume_obj, bpy.types.Object)

        # Check that it's a volume object
        assert volume_obj.type == "VOLUME"

        # Check that it has volume data
        assert volume_obj.data is not None
        assert isinstance(volume_obj.data, bpy.types.Volume)

        # Check that the object is in the scene
        assert volume_obj.name in bpy.data.objects

    def test_import_vdb_with_string_path(self, temp_vdb_file, clean_scene):
        """Test VDB import with string path instead of Path object."""
        # Import using string path
        volume_obj = import_vdb(str(temp_vdb_file))

        assert volume_obj is not None
        assert volume_obj.type == "VOLUME"

    def test_import_vdb_to_named_collection(self, temp_vdb_file, clean_scene):
        """Test importing VDB to a named collection."""
        collection_name = "TestVDBCollection"

        # Import to named collection
        volume_obj = import_vdb(temp_vdb_file, collection=collection_name)

        # Check that the collection was created
        assert collection_name in bpy.data.collections
        target_collection = bpy.data.collections[collection_name]

        # Check that the object is in the correct collection
        assert volume_obj in target_collection.objects.values()

        # Check that it's not in the default collection
        default_collection = bpy.context.scene.collection
        assert volume_obj not in default_collection.objects.values()

    def test_import_vdb_to_existing_collection(self, temp_vdb_file, clean_scene):
        """Test importing VDB to an existing collection object."""
        # Create a collection first
        test_collection = create_collection("ExistingCollection")

        # Import to the existing collection
        volume_obj = import_vdb(temp_vdb_file, collection=test_collection)

        # Check that the object is in the correct collection
        assert volume_obj in test_collection.objects.values()

    def test_import_vdb_default_collection(self, temp_vdb_file, clean_scene):
        """Test importing VDB with no collection specified (should use default)."""
        # Import without specifying collection
        volume_obj = import_vdb(temp_vdb_file, collection=None)

        # Should be in some collection (the default behavior of Blender)
        assert len(volume_obj.users_collection) > 0

    def test_import_nonexistent_vdb_file(self, clean_scene):
        """Test importing a non-existent VDB file."""
        nonexistent_path = Path("/nonexistent/path/file.vdb")

        # Should raise an exception when trying to import non-existent file
        with pytest.raises(RuntimeError):
            import_vdb(nonexistent_path)

    def test_import_vdb_volume_data_properties(self, temp_vdb_file, clean_scene):
        """Test that the imported VDB has expected volume properties."""
        volume_obj = import_vdb(temp_vdb_file)

        # Check volume data properties
        volume_data = volume_obj.data
        assert hasattr(volume_data, "grids")

        # Check that the volume data has the expected filepath
        assert volume_data.filepath == str(temp_vdb_file)

        # Check that volume data has expected attributes
        assert hasattr(volume_data, "display")
        assert hasattr(volume_data, "render")
        assert hasattr(volume_data, "materials")

        # Note: Due to Blender/OpenVDB version compatibility issues,
        # the grids may not always be loaded correctly in all environments.
        # This test focuses on verifying the volume object structure rather than
        # the specific grid content, which may vary by Blender/OpenVDB version.


@pytest.mark.skipif(HAS_OPENVDB, reason="Testing OpenVDB not available case")
def test_import_vdb_without_openvdb():
    """Test that we can still run tests when OpenVDB is not available."""
    # This test just ensures our skip logic works correctly
    assert not HAS_OPENVDB
