import tempfile
from pathlib import Path
from typing import Any

import bpy
import pytest

import databpy as db
from databpy.nodes import (
    NodeGroupCreationError,
    custom_string_iswitch,
    input_socket,
    new_socket,
    socket_value,
    tree_interface,
)


def _get_iswitch(tree: bpy.types.NodeTree) -> bpy.types.GeometryNodeIndexSwitch:
    return next(
        node
        for node in tree.nodes
        if isinstance(node, bpy.types.GeometryNodeIndexSwitch)
    )


def _new_group_node(tree: bpy.types.NodeTree) -> bpy.types.GeometryNodeGroup:
    node = tree.nodes.new("GeometryNodeGroup")
    assert isinstance(node, bpy.types.GeometryNodeGroup)
    return node


def test_custom_string_iswitch_basic():
    """Test basic creation of string index switch node group"""

    tree = custom_string_iswitch("TestSwitch", ["X", "Y", "Z"])

    assert tree.name == "TestSwitch"
    assert isinstance(tree, bpy.types.NodeTree)

    # Test input/output sockets
    socket_in = tree_interface(tree).items_tree["attr_id"]
    assert isinstance(socket_in, bpy.types.NodeTreeInterfaceSocket)
    assert socket_in.in_out == "INPUT"
    socket_out = tree_interface(tree).items_tree["String"]
    assert isinstance(socket_out, bpy.types.NodeTreeInterfaceSocket)
    assert socket_out.in_out == "OUTPUT"

    # Test node presence and configuration
    iswitch = _get_iswitch(tree)
    assert iswitch.data_type == "STRING"
    assert len(iswitch.index_switch_items) == 3


def test_custom_string_iswitch_values():
    """Test that input values are correctly assigned"""
    values = ["Chain_A", "Chain_B", "Chain_C", "Chain_D"]
    tree = custom_string_iswitch("ValueTest", values, "chain")

    iswitch = _get_iswitch(tree)

    # Check all values are assigned correctly
    for i, val in enumerate(values):
        assert socket_value(input_socket(iswitch, i + 1)) == val


def test_custom_string_iswitch_name_duplication():
    """Test that existing node group is returned if name exists"""
    tree1 = custom_string_iswitch("ReuseTest", ["A", "B"])
    tree2 = custom_string_iswitch("ReuseTest", ["X", "Y"])

    assert tree1.name == "ReuseTest"
    assert tree1.name + ".001" == tree2.name


def test_custom_string_iswitch_minimal():
    """Test creation with default values"""
    tree = custom_string_iswitch("MinimalTest", ["A", "B", "C"])

    iswitch = _get_iswitch(tree)
    assert len(iswitch.index_switch_items) == 3
    assert socket_value(input_socket(iswitch, 1)) == "A"
    assert socket_value(input_socket(iswitch, 2)) == "B"
    assert socket_value(input_socket(iswitch, 3)) == "C"


def test_long_list():
    """Test that a long list of values is correctly handled"""
    tree = custom_string_iswitch(
        "LongListTest", [str(x) for x in range(1_000)], "chain"
    )
    iswitch = tree.nodes["Index Switch"]
    for i, val in enumerate(range(1_000)):
        assert socket_value(input_socket(iswitch, i + 1)) == str(val)


def test_raises_error():
    """Test that an error is raised if the node group already exists"""
    int_values: Any = range(10)
    with pytest.raises(NodeGroupCreationError):
        custom_string_iswitch("TestSwitch", int_values)


def test_input_output():
    tree = db.nodes.new_tree()
    new_socket(tree, "test_int", in_out="INPUT", socket_type="NodeSocketInt")
    new_socket(tree, "test_float", in_out="INPUT", socket_type="NodeSocketFloat")
    new_socket(tree, "test_int1", in_out="INPUT", socket_type="NodeSocketInt")

    group1 = db.nodes.new_tree("Group1")
    new_socket(group1, "test_float", in_out="INPUT", socket_type="NodeSocketFloat")
    new_socket(group1, "test_int", in_out="INPUT", socket_type="NodeSocketInt")
    new_socket(group1, "test_int1", in_out="INPUT", socket_type="NodeSocketInt")

    group2 = db.nodes.new_tree("Group2")
    new_socket(group2, "test_float", in_out="INPUT", socket_type="NodeSocketFloat")
    new_socket(group2, "test_int", in_out="INPUT", socket_type="NodeSocketInt")
    new_socket(group2, "test_int2", in_out="INPUT", socket_type="NodeSocketInt")

    node = _new_group_node(tree)
    node.node_tree = group1
    tree.links.new(
        db.nodes.get_input(tree).outputs["Geometry"],
        node.inputs["Geometry"],
    )
    tree.links.new(
        node.outputs["Geometry"],
        db.nodes.get_output(tree).inputs["Geometry"],
    )
    for name in ["test_int", "test_float", "test_int1"]:
        tree.links.new(
            db.nodes.get_input(tree).outputs[name],
            node.inputs[name],
        )

    assert "test_int1" in node.inputs
    assert node.inputs["test_int1"].is_linked

    with db.nodes.MaintainConnections(node):
        node.node_tree = group2

    assert node.inputs["Geometry"].is_linked
    assert node.inputs["test_float"].is_linked
    assert node.inputs["test_int"].is_linked
    assert "test_int1" not in node.inputs
    assert not node.inputs["test_int2"].is_linked


def test_duplicate_prevention():
    tree = db.nodes.new_tree()
    new_socket(tree, "test_int", in_out="INPUT", socket_type="NodeSocketInt")
    new_socket(tree, "test_float", in_out="INPUT", socket_type="NodeSocketFloat")
    new_socket(tree, "test_int1", in_out="INPUT", socket_type="NodeSocketInt")

    group1 = db.nodes.new_tree("Group1")
    new_socket(group1, "test_float", in_out="INPUT", socket_type="NodeSocketFloat")
    new_socket(group1, "test_int", in_out="INPUT", socket_type="NodeSocketInt")
    new_socket(group1, "test_int1", in_out="INPUT", socket_type="NodeSocketInt")

    group2 = db.nodes.new_tree("Group2")
    new_socket(group2, "test_float", in_out="INPUT", socket_type="NodeSocketFloat")
    new_socket(group2, "test_int", in_out="INPUT", socket_type="NodeSocketInt")
    new_socket(group2, "test_int2", in_out="INPUT", socket_type="NodeSocketInt")

    node = _new_group_node(tree)
    node.node_tree = group1
    tree.links.new(
        db.nodes.get_input(tree).outputs["Geometry"],
        node.inputs["Geometry"],
    )
    tree.links.new(
        node.outputs["Geometry"],
        db.nodes.get_output(tree).inputs["Geometry"],
    )
    for name in ["test_int", "test_float", "test_int1"]:
        tree.links.new(
            db.nodes.get_input(tree).outputs[name],
            node.inputs[name],
        )
    assert len(bpy.data.node_groups) == 3
    group1.copy()
    assert len(bpy.data.node_groups) == 4
    with db.nodes.DuplicatePrevention(timing=True):
        tree2 = db.require(tree.copy(), "Failed to copy the node tree")
        for _ in range(10):
            group = _new_group_node(tree2)
            group.node_tree = db.require(group1.copy(), "Failed to copy the group")

    assert len(bpy.data.node_groups) == 4


@pytest.mark.parametrize("suffix", ["NodeTree", ""])
def test_append_from_blend(suffix):
    # we have to use the test node group on an object/ modifier otherwise it will get
    # cleaned up by Blener when we save and exit the file
    tree = db.nodes.custom_string_iswitch("TestSwitch", ["A", "B", "C", "D"])
    obj = bpy.data.objects["Cube"]
    modifier = obj.modifiers.new(type="NODES", name="Modifier")
    assert isinstance(modifier, bpy.types.NodesModifier)
    modifier.node_group = tree
    assert bpy.data.node_groups.get("TestSwitch")
    # save the blend file in a temp file
    with tempfile.NamedTemporaryFile(suffix=".blend") as f:
        # save the current working Blender file and reload a fresh one, which doesn't
        # contain any node groups
        bpy.ops.wm.save_as_mainfile(filepath=f.name)
        bpy.ops.wm.read_homefile("EXEC_DEFAULT")
        assert not bpy.data.node_groups.get("TestSwitch")

        # test appending the node group from the save .blend file into the current one
        tree2 = db.nodes.append_from_blend("TestSwitch", Path(f.name) / suffix)
        assert tree2.name == "TestSwitch"
        assert len(tree2.nodes) == 3
        iswitch = tree2.nodes["Index Switch"]
        assert socket_value(input_socket(iswitch, 1)) == "A"
        assert socket_value(input_socket(iswitch, 2)) == "B"
        assert socket_value(input_socket(iswitch, 3)) == "C"
        assert socket_value(input_socket(iswitch, 4)) == "D"
