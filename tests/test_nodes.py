import pytest
import bpy
import databpy as db
from databpy.nodes import custom_string_iswitch, NodeGroupCreationError


def test_custom_string_iswitch_basic():
    """Test basic creation of string index switch node group"""

    tree = custom_string_iswitch("TestSwitch", ["X", "Y", "Z"])

    assert tree.name == "TestSwitch"
    assert isinstance(tree, bpy.types.NodeTree)

    # Test input/output sockets
    assert tree.interface.items_tree["attr_id"].in_out == "INPUT"
    assert tree.interface.items_tree["String"].in_out == "OUTPUT"

    # Test node presence and configuration
    iswitch = next(n for n in tree.nodes if n.type == "INDEX_SWITCH")
    assert iswitch.data_type == "STRING"
    assert len(iswitch.index_switch_items) == 3


def test_custom_string_iswitch_values():
    """Test that input values are correctly assigned"""
    values = ["Chain_A", "Chain_B", "Chain_C", "Chain_D"]
    tree = custom_string_iswitch("ValueTest", values, "chain")

    iswitch = next(n for n in tree.nodes if n.type == "INDEX_SWITCH")

    # Check all values are assigned correctly
    for i, val in enumerate(values):
        assert iswitch.inputs[i + 1].default_value == val


def test_custom_string_iswitch_name_duplication():
    """Test that existing node group is returned if name exists"""
    tree1 = custom_string_iswitch("ReuseTest", ["A", "B"])
    tree2 = custom_string_iswitch("ReuseTest", ["X", "Y"])

    assert tree1.name == "ReuseTest"
    assert tree1.name + ".001" == tree2.name


def test_custom_string_iswitch_minimal():
    """Test creation with default values"""
    tree = custom_string_iswitch("MinimalTest", ["A", "B", "C"])

    iswitch = next(n for n in tree.nodes if n.type == "INDEX_SWITCH")
    assert len(iswitch.index_switch_items) == 3
    assert iswitch.inputs[1].default_value == "A"
    assert iswitch.inputs[2].default_value == "B"
    assert iswitch.inputs[3].default_value == "C"


def test_long_list():
    """Test that a long list of values is correctly handled"""
    tree = custom_string_iswitch(
        "LongListTest", [str(x) for x in range(1_000)], "chain"
    )
    for i, val in enumerate(range(1_000)):
        assert tree.nodes["Index Switch"].inputs[i + 1].default_value == str(val)


def test_raises_error():
    """Test that an error is raised if the node group already exists"""
    with pytest.raises(NodeGroupCreationError):
        custom_string_iswitch("TestSwitch", range(10))
