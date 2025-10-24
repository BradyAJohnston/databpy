import pytest
import numpy as np
import bpy
import databpy as db
import itertools


def test_attribute_properties():
    # Create test object with known vertices
    verts = np.array([[0, 0, 0], [1, 1, 1], [2, 2, 2]])
    obj = db.create_object(verts, name="TestObject")
    att = db.Attribute(obj.data.attributes["position"])
    assert att.name == "position"
    assert att.type_name == "FLOAT_VECTOR"
    att = db.store_named_attribute(
        obj, np.random.rand(3, 3), "test_attr", domain="POINT"
    )
    assert att.name == "test_attr"


def test_errores():
    # Create test object with known vertices
    verts = np.array([[0, 0, 0], [1, 1, 1], [2, 2, 2]])
    obj = db.create_object(verts, name="TestObject")
    db.Attribute(obj.data.attributes["position"])
    with pytest.raises(ValueError):
        db.store_named_attribute(
            obj, np.random.rand(3, 3), "test_attr", domain="FAKE_DOMAIN"
        )
    with pytest.raises(ValueError):
        db.store_named_attribute(
            obj, np.random.rand(3, 3), "test_attr", atype="FAKE_TYPE"
        )
    with pytest.raises(db.NamedAttributeError):
        db.remove_named_attribute(obj, "nonexistent_attr")


def test_named_attribute_position():
    # Create test object with known vertices
    verts = np.array([[0, 0, 0], [1, 1, 1], [2, 2, 2]])
    obj = db.create_object(verts, name="TestObject")

    # Test retrieving position attribute
    result = db.named_attribute(obj, "position")
    np.testing.assert_array_equal(result, verts)


def test_named_attribute_custom():
    # Create test object
    verts = np.array([[0, 0, 0], [1, 1, 1]])
    obj = db.create_object(verts, name="TestObject")

    # Store custom attribute
    test_data = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    db.store_named_attribute(obj, test_data, "test_attr")

    # Test retrieving custom attribute
    result = db.named_attribute(obj, "test_attr")
    np.testing.assert_array_equal(result, test_data)

    db.remove_named_attribute(obj, "test_attr")
    with pytest.raises(db.NamedAttributeError):
        db.named_attribute(obj, "test_attr")


def test_named_attribute_nonexistent():
    obj = db.create_object(np.array([[0, 0, 0]]), name="TestObject")

    with pytest.raises(AttributeError):
        db.named_attribute(obj, "nonexistent_attr")


def test_attribute_mismatch():
    # Create test object
    verts = np.array([[0, 0, 0], [1, 1, 1]])
    obj = db.create_object(verts, name="TestObject")
    new_data = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    db.store_named_attribute(obj, new_data, "test_attr")

    test_data = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 1.0, 0.0]])

    with pytest.raises(db.NamedAttributeError):
        db.store_named_attribute(obj, test_data, "test_attr")

    with pytest.raises(db.NamedAttributeError):
        db.store_named_attribute(obj, np.repeat(1, 3), "test_attr")


def test_attribute_overwrite():
    verts = np.array([[0, 0, 0], [1, 1, 1]])
    obj = db.create_object(verts, name="TestObject")
    new_data = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    db.store_named_attribute(obj, new_data, "test_attr")
    # with overwrite = False, the attribute should not be overwritten and a new one will
    # be created with a new name instead
    new_values = np.repeat(1, 2)
    att = db.store_named_attribute(obj, new_values, "test_attr", overwrite=False)

    assert new_values.shape != db.named_attribute(obj, "test_attr").shape
    assert np.allclose(new_values, db.named_attribute(obj, att.name))

    assert db.named_attribute(obj, "test_attr").shape == (2, 3)
    with pytest.raises(db.NamedAttributeError):
        db.store_named_attribute(obj, new_values, "test_attr")

    db.remove_named_attribute(obj, "test_attr")
    with pytest.raises(db.NamedAttributeError):
        db.named_attribute(obj, "test_attr")
    db.store_named_attribute(obj, new_values, "test_attr")
    assert np.allclose(db.named_attribute(obj, "test_attr"), new_values)
    assert db.named_attribute(obj, "test_attr").shape == (2,)


def test_named_attribute_evaluate():
    # Create test object with modifier
    obj = bpy.data.objects["Cube"]
    pos = db.named_attribute(obj, "position")

    # Add a simple modifier (e.g., subdivision surface)
    mod = obj.modifiers.new(name="Subsurf", type="SUBSURF")
    mod.levels = 1

    # Test with evaluate=True
    result = db.named_attribute(obj, "position", evaluate=True)
    assert len(result) > len(pos)  # Should have more vertices after subdivision


def test_obj_type_error():
    with pytest.raises(TypeError):
        db.named_attribute(123, "position")

    with pytest.raises(TypeError):
        db.named_attribute(bpy.data.objects["Camera"], "position")


def test_check_obj():
    db.attribute._check_obj_attributes(bpy.data.objects["Cube"])
    assert pytest.raises(
        TypeError,
        db.attribute._check_obj_attributes,
        bpy.data.objects["Camera"],
    )
    assert pytest.raises(
        TypeError,
        db.attribute._check_obj_attributes,
        bpy.data.objects["Light"],
    )
    assert pytest.raises(
        TypeError,
        db.attribute._check_is_mesh,
        bpy.data.objects["Light"],
    )
    assert pytest.raises(
        TypeError,
        db.attribute._check_is_mesh,
        bpy.data.objects["Camera"],
    )


def test_guess_attribute_type():
    # Create test object
    np.array([[0, 0, 0], [1, 1, 1]])
    assert pytest.raises(
        ValueError,
        db.attribute.guess_atype_from_array,
        ["A", "B", "C"],
    )


def test_guess_atype():
    """Test attribute type guessing from array shape and dtype."""
    # Test float-based types
    assert db.attribute.AttributeTypes.FLOAT == db.attribute.guess_atype_from_array(
        np.zeros(10, dtype=np.float32)
    )
    assert db.attribute.AttributeTypes.FLOAT == db.attribute.guess_atype_from_array(
        np.zeros(10, dtype=np.float64)
    )
    assert db.attribute.AttributeTypes.FLOAT2 == db.attribute.guess_atype_from_array(
        np.zeros((10, 2), dtype=np.float32)
    )
    assert (
        db.attribute.AttributeTypes.FLOAT_VECTOR
        == db.attribute.guess_atype_from_array(np.zeros((10, 3)))
    )
    assert (
        db.attribute.AttributeTypes.FLOAT_COLOR
        == db.attribute.guess_atype_from_array(np.zeros((10, 4)))
    )
    assert db.attribute.AttributeTypes.FLOAT4X4 == db.attribute.guess_atype_from_array(
        np.zeros((10, 4, 4))
    )

    # Test integer-based types
    assert db.attribute.AttributeTypes.INT == db.attribute.guess_atype_from_array(
        np.zeros(10, dtype=np.int32)
    )
    assert db.attribute.AttributeTypes.INT == db.attribute.guess_atype_from_array(
        np.zeros(10, dtype=np.int64)
    )
    assert db.attribute.AttributeTypes.INT8 == db.attribute.guess_atype_from_array(
        np.zeros(10, dtype=np.int8)
    )
    assert db.attribute.AttributeTypes.INT8 == db.attribute.guess_atype_from_array(
        np.zeros(10, dtype=np.uint8)
    )
    assert db.attribute.AttributeTypes.INT32_2D == db.attribute.guess_atype_from_array(
        np.zeros((10, 2), dtype=np.int32)
    )

    # Test color types - distinguishes byte vs float based on dtype
    assert (
        db.attribute.AttributeTypes.BYTE_COLOR
        == db.attribute.guess_atype_from_array(np.zeros((10, 4), dtype=np.uint8))
    )
    assert (
        db.attribute.AttributeTypes.FLOAT_COLOR
        == db.attribute.guess_atype_from_array(np.zeros((10, 4), dtype=np.float32))
    )

    # Test boolean
    assert db.attribute.AttributeTypes.BOOLEAN == db.attribute.guess_atype_from_array(
        np.zeros(10, dtype=bool)
    )


def test_raise_error():
    with pytest.raises(db.NamedAttributeError):
        db.store_named_attribute(bpy.data.objects["Cube"], np.zeros((10, 3)), "test")

    with pytest.raises(db.NamedAttributeError):
        db.remove_named_attribute(bpy.data.objects["Cube"], "testing")


def test_named_attribute_name(snapshot):
    obj = bpy.data.objects["Cube"]
    for i in range(150):
        name = "a" * i
        print(f"{i} letters, name: '{name}'")
        data = np.random.rand(len(obj.data.vertices), 3)
        if i >= 68 or i == 0:
            with pytest.raises(db.NamedAttributeError):
                db.store_named_attribute(obj, data, name)
        else:
            db.store_named_attribute(obj, data, name)
            assert name in db.list_attributes(obj)

    assert snapshot == db.list_attributes(obj)


@pytest.mark.parametrize(
    "evaluate, drop_hidden", itertools.product([True, False], repeat=2)
)
def test_list_attributes(snapshot, evaluate, drop_hidden):
    obj = bpy.data.objects["Cube"]
    attrs = db.list_attributes(obj, evaluate=evaluate, drop_hidden=drop_hidden)
    assert snapshot == attrs

    # 10 different random string names with different lengths
    names = [
        "attr1",
        "longer_attribute_name",
        "a",
        "short",
        "medium_length",
        "x" * 50,
        "attr_with_special_chars!@#$%^&*()",
        "数字属性",
    ]

    # store a named attribute via geometry nodes as this should only show up
    # when evaluate=True
    tree = db.nodes.new_tree()
    n = tree.nodes.new("GeometryNodeStoreNamedAttribute")
    n.inputs["Name"].default_value = "testing"
    n.inputs["Value"].default_value = 0.5
    tree.links.new(tree.nodes["Group Input"].outputs["Geometry"], n.inputs["Geometry"])
    tree.links.new(n.outputs["Geometry"], tree.nodes["Group Output"].inputs["Geometry"])
    mod = obj.modifiers.new("db_nodes", "NODES")
    mod.node_group = tree

    for name in names:
        data = np.random.rand(len(obj.data.vertices), 3)
        db.store_named_attribute(obj, data, name, domain="POINT", atype="FLOAT_VECTOR")

    attributes = db.list_attributes(obj, evaluate=evaluate, drop_hidden=drop_hidden)
    assert attributes == db.BlenderObject(obj).list_attributes(
        evaluate=evaluate, drop_hidden=drop_hidden
    )
    assert snapshot == attributes

    if evaluate:
        assert "testing" in db.list_attributes(obj, evaluate=True)
    else:
        assert "testing" not in db.list_attributes(obj, evaluate=False)


def test_str_access_attribute():
    # Create test object with known vertices
    verts = np.array([[0, 0, 0], [1, 1, 1], [2, 2, 2]])
    bob = db.create_bob(verts)

    bob.store_named_attribute(np.array(range(9)).reshape((3, 3)), "test_name")
    assert isinstance(bob["test_name"], db.array.AttributeArray)
    assert bob["test_name"][0][0] == 0.0
    bob["test_name"][0] = 1
    assert bob["test_name"][0][0] == 1

    values = np.zeros(3, dtype=int)

    bob["another_name"] = values
    np.testing.assert_array_equal(bob["another_name"], values)

    bob["another_name"] = values + 10
    assert np.array_equal(bob["another_name"], values + 10)


def test_int32_dtype():
    """Test that INT attributes return int32 dtype, not int64."""
    verts = np.array([[0, 0, 0], [1, 1, 1], [2, 2, 2]])
    obj = db.create_object(verts, name="TestIntDtype")

    # Store an INT attribute
    int_data = np.array([1, 2, 3], dtype=np.int32)
    db.store_named_attribute(obj, int_data, "test_int", atype="INT")

    # Retrieve and verify it's int32, not int64
    result = db.named_attribute(obj, "test_int")
    assert result.dtype == np.int32, f"Expected int32, got {result.dtype}"
    np.testing.assert_array_equal(result, int_data)


def test_int32_2d_dtype():
    """Test that INT32_2D attributes return int32 dtype."""
    verts = np.array([[0, 0, 0], [1, 1, 1], [2, 2, 2]])
    obj = db.create_object(verts, name="TestInt2DDtype")

    # Store an INT32_2D attribute
    int_data = np.array([[1, 2], [3, 4], [5, 6]], dtype=np.int32)
    db.store_named_attribute(obj, int_data, "test_int2d", atype="INT32_2D")

    # Retrieve and verify it's int32
    result = db.named_attribute(obj, "test_int2d")
    assert result.dtype == np.int32, f"Expected int32, got {result.dtype}"
    np.testing.assert_array_equal(result, int_data)


def test_int8_dtype():
    """Test that INT8 attributes return int8 dtype."""
    verts = np.array([[0, 0, 0], [1, 1, 1], [2, 2, 2]])
    obj = db.create_object(verts, name="TestInt8Dtype")

    # Store an INT8 attribute
    int_data = np.array([1, 2, 3], dtype=np.int8)
    db.store_named_attribute(obj, int_data, "test_int8", atype="INT8")

    # Retrieve and verify it's int8
    result = db.named_attribute(obj, "test_int8")
    assert result.dtype == np.int8, f"Expected int8, got {result.dtype}"
    np.testing.assert_array_equal(result, int_data)


def test_byte_color_dtype():
    """Test that BYTE_COLOR attributes return uint8 dtype."""
    verts = np.array([[0, 0, 0], [1, 1, 1], [2, 2, 2]])
    obj = db.create_object(verts, name="TestByteColorDtype")

    # Store a BYTE_COLOR attribute (RGBA values as uint8)
    # BYTE_COLOR is stored as unsigned char in Blender (MLoopCol)
    color_data = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0]], dtype=np.uint8)
    db.store_named_attribute(obj, color_data, "test_byte_color", atype="BYTE_COLOR")

    # Retrieve and verify it's uint8
    result = db.named_attribute(obj, "test_byte_color")
    assert result.dtype == np.uint8, f"Expected uint8, got {result.dtype}"
    assert result.shape == (3, 4), f"Expected shape (3, 4), got {result.shape}"


def test_1d_array_reshaping():
    """Test that 1D arrays can be reshaped to match attribute dimensions."""
    verts = np.array([[0, 0, 0], [1, 1, 1], [2, 2, 2]])
    obj = db.create_object(verts, name="TestReshape")

    # Test with FLOAT_VECTOR (3D) - pass 1D array of 9 elements
    flat_data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9], dtype=np.float32)
    db.store_named_attribute(
        obj, flat_data, "test_reshape_vector", atype="FLOAT_VECTOR"
    )

    result = db.named_attribute(obj, "test_reshape_vector")
    assert result.shape == (3, 3), f"Expected shape (3, 3), got {result.shape}"
    np.testing.assert_array_equal(result, flat_data.reshape(3, 3))

    # Test with FLOAT2 - pass 1D array of 6 elements
    flat_data_2d = np.array([1, 2, 3, 4, 5, 6], dtype=np.float32)
    db.store_named_attribute(obj, flat_data_2d, "test_reshape_float2", atype="FLOAT2")

    result_2d = db.named_attribute(obj, "test_reshape_float2")
    assert result_2d.shape == (3, 2), f"Expected shape (3, 2), got {result_2d.shape}"
    np.testing.assert_array_equal(result_2d, flat_data_2d.reshape(3, 2))

    # Test with FLOAT_COLOR (4D) - pass 1D array of 12 elements
    flat_color = np.random.rand(12).astype(np.float32)
    db.store_named_attribute(obj, flat_color, "test_reshape_color", atype="FLOAT_COLOR")

    result_color = db.named_attribute(obj, "test_reshape_color")
    assert result_color.shape == (3, 4), (
        f"Expected shape (3, 4), got {result_color.shape}"
    )
    np.testing.assert_array_almost_equal(result_color, flat_color.reshape(3, 4))


def test_1d_array_wrong_size_fails():
    """Test that 1D arrays with wrong total size raise an error."""
    verts = np.array([[0, 0, 0], [1, 1, 1], [2, 2, 2]])
    obj = db.create_object(verts, name="TestReshapeFail")

    # Try to pass wrong size - should fail
    wrong_size = np.array([1, 2, 3, 4, 5], dtype=np.float32)  # 5 elements, need 9
    with pytest.raises(db.NamedAttributeError):
        db.store_named_attribute(
            obj, wrong_size, "test_wrong_size", atype="FLOAT_VECTOR"
        )


def test_attribute_from_array_reshaping():
    """Test that Attribute.from_array() can handle reshaping."""
    verts = np.array([[0, 0, 0], [1, 1, 1], [2, 2, 2]])
    obj = db.create_object(verts, name="TestAttrReshape")

    # Create attribute first
    initial_data = np.random.rand(3, 3).astype(np.float32)
    db.store_named_attribute(obj, initial_data, "test_attr_reshape")

    # Get the Attribute wrapper
    attr = db.Attribute(obj.data.attributes["test_attr_reshape"])

    # Try to set with 1D array
    flat_data = np.array([10, 11, 12, 13, 14, 15, 16, 17, 18], dtype=np.float32)
    attr.from_array(flat_data)

    # Verify it was reshaped correctly
    result = attr.as_array()
    assert result.shape == (3, 3)
    np.testing.assert_array_equal(result, flat_data.reshape(3, 3))
