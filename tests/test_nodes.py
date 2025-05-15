import tempfile
from pathlib import Path

import bpy
import pytest

import databpy as db
from databpy.nodes import NodeGroupCreationError, custom_string_iswitch


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


def test_input_output():
    tree = db.nodes.new_tree()
    tree.interface.new_socket("test_int", in_out="INPUT", socket_type="NodeSocketInt")
    tree.interface.new_socket(
        "test_float", in_out="INPUT", socket_type="NodeSocketFloat"
    )
    tree.interface.new_socket("test_int1", in_out="INPUT", socket_type="NodeSocketInt")

    group1 = db.nodes.new_tree("Group1")
    group1.interface.new_socket(
        "test_float", in_out="INPUT", socket_type="NodeSocketFloat"
    )
    group1.interface.new_socket("test_int", in_out="INPUT", socket_type="NodeSocketInt")
    group1.interface.new_socket(
        "test_int1", in_out="INPUT", socket_type="NodeSocketInt"
    )

    group2 = db.nodes.new_tree("Group2")
    group2.interface.new_socket(
        "test_float", in_out="INPUT", socket_type="NodeSocketFloat"
    )
    group2.interface.new_socket("test_int", in_out="INPUT", socket_type="NodeSocketInt")
    group2.interface.new_socket(
        "test_int2", in_out="INPUT", socket_type="NodeSocketInt"
    )

    node = tree.nodes.new("GeometryNodeGroup")
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
    tree.interface.new_socket("test_int", in_out="INPUT", socket_type="NodeSocketInt")
    tree.interface.new_socket(
        "test_float", in_out="INPUT", socket_type="NodeSocketFloat"
    )
    tree.interface.new_socket("test_int1", in_out="INPUT", socket_type="NodeSocketInt")

    group1 = db.nodes.new_tree("Group1")
    group1.interface.new_socket(
        "test_float", in_out="INPUT", socket_type="NodeSocketFloat"
    )
    group1.interface.new_socket("test_int", in_out="INPUT", socket_type="NodeSocketInt")
    group1.interface.new_socket(
        "test_int1", in_out="INPUT", socket_type="NodeSocketInt"
    )

    group2 = db.nodes.new_tree("Group2")
    group2.interface.new_socket(
        "test_float", in_out="INPUT", socket_type="NodeSocketFloat"
    )
    group2.interface.new_socket("test_int", in_out="INPUT", socket_type="NodeSocketInt")
    group2.interface.new_socket(
        "test_int2", in_out="INPUT", socket_type="NodeSocketInt"
    )

    node = tree.nodes.new("GeometryNodeGroup")
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
        tree2 = tree.copy()
        for _ in range(10):
            group = tree2.nodes.new("GeometryNodeGroup")
            group.node_tree = group1.copy()

    assert len(bpy.data.node_groups) == 5


@pytest.mark.parametrize("suffix", ["NodeTree", ""])
def test_append_from_blend(suffix):
    # we have to use the test node group on an object/ modifier otherwise it will get
    # cleaned up by Blener when we save and exit the file
    tree = db.nodes.custom_string_iswitch("TestSwitch", ["A", "B", "C", "D"])
    obj = bpy.data.objects["Cube"]
    obj.modifiers.new(type="NODES", name="Modifier").node_group = tree
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
        assert tree2.nodes["Index Switch"].inputs[1].default_value == "A"
        assert tree2.nodes["Index Switch"].inputs[2].default_value == "B"
        assert tree2.nodes["Index Switch"].inputs[3].default_value == "C"
        assert tree2.nodes["Index Switch"].inputs[4].default_value == "D"
