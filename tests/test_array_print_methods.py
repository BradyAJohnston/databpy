import pytest
import numpy as np
from databpy import create_object
from databpy.array import AttributeArray, ColumnAccessor, Attribute


class TestAttributeArrayPrintMethods:
    """Test the __str__ and __repr__ methods of AttributeArray."""

    @pytest.fixture
    def blender_object(self):
        """Create a real BlenderObject for testing."""
        obj = create_object(np.random.rand(10, 3).astype(np.float32), name="TestCube")
        return obj

    @pytest.fixture
    def example_attribute(self):
        """Create a real Attribute for testing."""
        obj = create_object(np.random.rand(10, 3).astype(np.float32), name="TestCube")
        return Attribute(obj.data.attributes["position"])

    @pytest.fixture
    def sample_array(self, blender_object):
        """Create a sample AttributeArray for testing."""
        # Create the AttributeArray using the real blender object
        return AttributeArray(blender_object, "position")

    def test_str_method_basic_info(self, sample_array):
        """Test that __str__ includes basic attribute information."""
        result = str(sample_array)

        # Check that all expected components are present
        assert "AttributeArray 'position'" in result
        assert "TestCube('TestCube')" in result
        assert "domain: POINT" in result

    def test_repr_method_detailed_info(self, sample_array):
        """Test that __repr__ includes detailed attribute information."""
        result = repr(sample_array)

        # Check that all expected components are present
        assert "AttributeArray(name='position'" in result
        assert "object='TestCube', mesh='TestCube" in result
        assert "domain=POINT" in result
        assert "type=FLOAT_VECTOR" in result

        # Check that array representation is included
        assert "array(" in result

    def test_str_method_different_array_shapes(self, blender_object):
        """Test __str__ method with different array shapes."""
        test_arrays = [
            np.array([1.0, 2.0, 3.0], dtype=np.float32),  # 1D
            np.array([[1.0, 2.0, 3.0]], dtype=np.float32),  # 2D single row
            np.array([[1.0], [2.0], [3.0]], dtype=np.float32),  # 2D single column
            np.array(
                [
                    [1.0, 2.0, 3.0, 4.0],
                    [5.0, 6.0, 7.0, 8.0],
                    [9.0, 10.0, 11.0, 12.0],
                    [13.0, 14.0, 15.0, 16.0],
                ],
                dtype=np.float32,
            ),  # 4x4 matrix
        ]

        for i, test_array in enumerate(test_arrays):
            # Create a new object for each test array with appropriate vertex count
            if test_array.ndim == 1:
                vertices = np.random.rand(len(test_array), 3).astype(np.float32)
            elif test_array.ndim == 2:
                vertices = np.random.rand(test_array.shape[0], 3).astype(np.float32)
            else:
                vertices = np.random.rand(test_array.shape[0], 3).astype(np.float32)

            obj = create_object(vertices, name=f"TestShape{i}")

            # Store the test array as a custom attribute
            from databpy.attribute import store_named_attribute

            store_named_attribute(
                obj,
                test_array,
                f"test_attr_{i}",
            )

            # Create AttributeArray for the custom attribute
            arr = AttributeArray(obj, f"test_attr_{i}")

            result = str(arr)
            # Check that the attribute name appears in the string representation
            assert f"test_attr_{i}" in result

    def test_print_integration(self, sample_array, capsys):
        """Test that print() works correctly with the __str__ method."""
        print(sample_array)
        captured = capsys.readouterr()

        assert "AttributeArray 'position'" in captured.out
        assert "TestCube('TestCube')" in captured.out
        assert "domain: POINT" in captured.out

    def test_str_method_with_large_array(self):
        """Test __str__ method with a large array to ensure it handles numpy's truncation."""
        # Create a large array that numpy will truncate
        large_vertices = np.random.rand(1000, 3).astype(np.float32)
        obj = create_object(large_vertices, name="LargeTestObject")

        # Get the position attribute array
        arr = AttributeArray(obj, "position")

        result = str(arr)
        assert "shape: (1000, 3)" in result

        # Should contain numpy's truncation indicator for large arrays
        assert "..." in result or len(result.split("\n")) > 1


class TestColumnAccessorPrintMethods:
    """Test print behavior of ColumnAccessor objects."""

    @pytest.fixture
    def parent_array_and_data(self):
        """Create a real parent AttributeArray with known data."""
        # Create object with known vertex positions
        parent_data = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]], dtype=np.float32)
        obj = create_object(parent_data, name="ColumnTestObject")

        # Get the position attribute as an AttributeArray
        parent_array = AttributeArray(obj, "position")

        return parent_array, parent_data

    def test_column_accessor_str_delegation(self, parent_array_and_data):
        """Test that ColumnAccessor properly delegates string operations."""
        parent_array, parent_data = parent_array_and_data

        # Create ColumnAccessor
        col_accessor = ColumnAccessor(parent_array, 1)  # Second column

        # The string representation should come from the column data
        expected_column = parent_data[:, 1]  # [2.0, 5.0]

        # Test that we can convert to string (should use numpy's default)
        result = str(np.asarray(col_accessor))
        expected = str(expected_column)

        assert result == expected

    def test_column_accessor_array_conversion(self, parent_array_and_data):
        """Test that ColumnAccessor converts to array properly for printing."""
        parent_array, parent_data = parent_array_and_data

        col_accessor = ColumnAccessor(parent_array, 0)  # First column

        # Convert to array and check it matches expected column
        as_array = np.asarray(col_accessor)
        expected_column = parent_data[:, 0]  # [1.0, 4.0]

        np.testing.assert_array_equal(as_array, expected_column)
