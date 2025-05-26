import pytest
import numpy as np
from unittest.mock import Mock
from databpy import create_bob
from databpy.array import AttributeArray, ColumnAccessor, Attribute
from databpy.attribute import AttributeTypes


class TestAttributeArrayPrintMethods:
    """Test the __str__ and __repr__ methods of AttributeArray."""

    @pytest.fixture
    def blender_object(self):
        """Create a mock BlenderObject for testing."""
        obj = create_bob(np.random.rand(10, 3).astype(np.float32), name="TestCube")
        return obj

    @pytest.fixture
    def example_attribute(self):
        """Create a mock Attribute for testing."""
        obj = create_bob(np.random.rand(10, 3).astype(np.float32), name="TestCube")
        return Attribute(obj.attributes()["position"])

    @pytest.fixture
    def sample_array(self, blender_object, example_attribute):
        """Create a sample AttributeArray for testing."""
        # Mock the Attribute constructor
        with pytest.MonkeyPatch().context() as m:
            m.setattr("databpy.array.Attribute", lambda x: example_attribute)

            # Create the AttributeArray
            arr = AttributeArray.__new__(AttributeArray, blender_object, "position")
            arr._blender_object = blender_object
            arr._attribute = example_attribute
            arr._name = "position"

            return arr

    def test_str_method_basic_info(self, sample_array):
        """Test that __str__ includes basic attribute information."""
        result = str(sample_array)

        # Check that all expected components are present
        assert "AttributeArray 'position'" in result
        assert "MESH 'TestCube'" in result
        assert "domain: POINT" in result

    def test_repr_method_detailed_info(self, sample_array):
        """Test that __repr__ includes detailed attribute information."""
        result = repr(sample_array)

        # Check that all expected components are present
        assert "AttributeArray(name='position'" in result
        assert "object='TestCube' (MESH)" in result
        assert "domain=POINT" in result
        assert "type=AttributeTypes.FLOAT_VECTOR" in result

        # Check that array representation is included
        assert "array(" in result

    def test_str_method_different_object_types(self, example_attribute):
        """Test __str__ method with different Blender object types."""
        # Test with different object types
        object_types = ["MESH", "CURVE", "SURFACE", "META", "FONT"]

        for obj_type in object_types:
            mock_obj = Mock()
            mock_obj.object = Mock()
            mock_obj.object.name = f"Test{obj_type}"
            mock_obj.object.type = obj_type

            arr = np.array([[1.0, 2.0, 3.0]], dtype=np.float32).view(AttributeArray)
            arr._blender_object = mock_obj
            arr._attribute = example_attribute
            arr._name = "test_attr"

            result = str(arr)
            assert f"{obj_type} 'Test{obj_type}'" in result

    def test_str_method_different_domains(self, blender_object):
        """Test __str__ method with different attribute domains."""
        domains = ["POINT", "EDGE", "FACE", "CORNER"]

        for domain_name in domains:
            mock_attr = Mock()
            mock_attr.domain = Mock()
            mock_attr.domain.name = domain_name
            mock_attr.atype = AttributeTypes.FLOAT_VECTOR

            arr = np.array([[1.0, 2.0, 3.0]], dtype=np.float32).view(AttributeArray)
            arr._blender_object = blender_object
            arr._attribute = mock_attr
            arr._name = "test_attr"

            result = str(arr)
            assert f"domain: {domain_name}" in result

    def test_str_method_different_array_shapes(self, blender_object, example_attribute):
        """Test __str__ method with different array shapes."""
        test_arrays = [
            np.array([1.0, 2.0, 3.0], dtype=np.float32),  # 1D
            np.array([[1.0, 2.0, 3.0]], dtype=np.float32),  # 2D single row
            np.array([[1.0], [2.0], [3.0]], dtype=np.float32),  # 2D single column
            np.array([[[1.0, 2.0]], [[3.0, 4.0]]], dtype=np.float32),  # 3D
        ]

        for test_array in test_arrays:
            arr = test_array.view(AttributeArray)
            arr._blender_object = blender_object
            arr._attribute = example_attribute
            arr._name = "test_attr"

            result = str(arr)
            assert f"shape: {test_array.shape}" in result

    def test_repr_method_different_attribute_types(self, blender_object):
        """Test __repr__ method with different attribute types."""
        attr_types = [
            AttributeTypes.FLOAT_VECTOR,
            AttributeTypes.FLOAT_COLOR,
        ]

        for attr_type in attr_types:
            mock_attr = Mock()
            mock_attr.domain = Mock()
            mock_attr.domain.name = "POINT"
            mock_attr.atype = attr_type

            arr = np.array([[1.0, 2.0, 3.0]], dtype=np.float32).view(AttributeArray)
            arr._blender_object = blender_object
            arr._attribute = mock_attr
            arr._name = "test_attr"

            result = repr(arr)
            assert f"type={attr_type}" in result

    def test_print_integration(self, sample_array, capsys):
        """Test that print() works correctly with the __str__ method."""
        print(sample_array)
        captured = capsys.readouterr()

        assert "AttributeArray 'position'" in captured.out
        assert "MESH 'TestCube'" in captured.out
        assert "domain: POINT" in captured.out

    def test_str_method_with_large_array(self, blender_object, example_attribute):
        """Test __str__ method with a large array to ensure it handles numpy's truncation."""
        # Create a large array that numpy will truncate
        large_array = np.random.rand(1000, 3).astype(np.float32)

        arr = large_array.view(AttributeArray)
        arr._blender_object = blender_object
        arr._attribute = example_attribute

        result = str(arr)
        assert "shape: (1000, 3)" in result

        # Should contain numpy's truncation indicator for large arrays
        assert "..." in result or len(result.split("\n")) > 1

    def test_str_method_preserves_numpy_formatting(
        self, blender_object, example_attribute
    ):
        """Test that __str__ preserves numpy's array formatting."""
        # Test with specific values that have known string representations
        test_array = np.array(
            [[1.0, 2.5, 3.14159], [0.0, -1.5, 2.71828]], dtype=np.float32
        )

        arr = test_array.view(AttributeArray)
        arr._blender_object = blender_object
        arr._attribute = example_attribute
        arr._name = "test_attr"

        result = str(arr)
        numpy_str = np.array_str(test_array)

        # The numpy array string should be contained in our result
        assert numpy_str in result

    def test_repr_method_preserves_numpy_formatting(
        self, blender_object, example_attribute
    ):
        """Test that __repr__ preserves numpy's array representation."""
        test_array = np.array(
            [[1.0, 2.5, 3.14159], [0.0, -1.5, 2.71828]], dtype=np.float32
        )

        arr = test_array.view(AttributeArray)
        arr._blender_object = blender_object
        arr._attribute = example_attribute
        arr._name = "test_attr"

        result = repr(arr)
        numpy_repr = np.array_repr(test_array)

        # The numpy array representation should be contained in our result
        assert numpy_repr in result


class TestColumnAccessorPrintMethods:
    """Test print behavior of ColumnAccessor objects."""

    @pytest.fixture
    def mock_parent_array(self):
        """Create a mock parent AttributeArray."""
        parent = Mock()
        parent_data = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]], dtype=np.float32)
        parent.__array__ = Mock(return_value=parent_data)
        return parent, parent_data

    def test_column_accessor_str_delegation(self, mock_parent_array):
        """Test that ColumnAccessor properly delegates string operations."""
        parent, parent_data = mock_parent_array

        # Create ColumnAccessor
        col_accessor = ColumnAccessor(parent, 1)  # Second column

        # The string representation should come from the column data
        expected_column = parent_data[:, 1]  # [2.0, 5.0]

        # Test that we can convert to string (should use numpy's default)
        result = str(np.asarray(col_accessor))
        expected = str(expected_column)

        assert result == expected

    def test_column_accessor_array_conversion(self, mock_parent_array):
        """Test that ColumnAccessor converts to array properly for printing."""
        parent, parent_data = mock_parent_array

        col_accessor = ColumnAccessor(parent, 0)  # First column

        # Convert to array and check it matches expected column
        as_array = np.asarray(col_accessor)
        expected_column = parent_data[:, 0]  # [1.0, 4.0]

        np.testing.assert_array_equal(as_array, expected_column)
