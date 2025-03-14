import bpy
from .utils import MaintainConnections, NodeGroupCreationError, get_input, get_output
from typing import Iterable


def swap_tree(node: bpy.types.GeometryNode, tree: bpy.types.GeometryNodeTree) -> None:
    with MaintainConnections(node):
        node.node_tree = tree  # type: ignore
        node.name = tree.name


def new_tree(
    name: str = "Geometry Nodes",
    geometry: bool = True,
    input_name: str = "Geometry",
    output_name: str = "Geometry",
    fallback: bool = True,
) -> bpy.types.NodeTree:
    tree = bpy.data.node_groups.get(name)
    # if the group already exists, return it and don't create a new one
    if tree and fallback:
        return tree

    # create a new group for this particular name and do some initial setup
    tree = bpy.data.node_groups.new(name, "GeometryNodeTree")
    input_node = tree.nodes.new("NodeGroupInput")
    output_node = tree.nodes.new("NodeGroupOutput")
    input_node.location.x = -200 - input_node.width
    output_node.location.x = 200
    if geometry:
        tree.interface.new_socket(
            input_name, in_out="INPUT", socket_type="NodeSocketGeometry"
        )
        tree.interface.new_socket(
            output_name, in_out="OUTPUT", socket_type="NodeSocketGeometry"
        )
        tree.links.new(output_node.inputs[0], input_node.outputs[0])
    return tree


def custom_string_iswitch(
    name: str, values: Iterable[str], attr_name: str = "attr_id"
) -> bpy.types.NodeTree:
    """
    Creates a node group containing a `Index Switch` node with all the given values.
    """

    # dont' attempt to return an already existing node tree. If a user is requesting a
    # new one they are likely passing in a new list, so we have to createa a new one
    # to ensure we are using the new iterables
    tree = new_tree(name=name, geometry=False, fallback=False)
    # name might have originally been the same, but on creation it might be name.001 or
    # something similar so we just grab the name from the tree
    name = tree.name
    tree.color_tag = "CONVERTER"

    # try creating the node group, otherwise on fail cleanup the created group and
    # report the error
    try:
        link = tree.links.new
        node_input = get_input(tree)
        socket_in = tree.interface.new_socket(
            attr_name, in_out="INPUT", socket_type="NodeSocketInt"
        )
        socket_in.name = attr_name
        node_output = get_output(tree)
        socket_out = tree.interface.new_socket(
            attr_name, in_out="OUTPUT", socket_type="NodeSocketString"
        )
        socket_out.name = "String"

        node_iswitch: bpy.types.GeometryNodeIndexSwitch = tree.nodes.new(  # type: ignore
            "GeometryNodeIndexSwitch"
        )
        node_iswitch.data_type = "STRING"
        link(node_input.outputs[socket_in.identifier], node_iswitch.inputs["Index"])

        for i, item in enumerate(values):
            # the node starts with 2 items alread, so we only create new items
            # if they are above that
            if i > 1:
                node_iswitch.index_switch_items.new()

            node_iswitch.inputs[int(i + 1)].default_value = item

        link(
            node_iswitch.outputs["Output"],
            node_output.inputs[socket_out.identifier],
        )

        return tree

    # if something broke when creating the node group, delete whatever was created
    except Exception as e:
        node_name = tree.name
        bpy.data.node_groups.remove(tree)
        raise NodeGroupCreationError(
            f"Unable to make node group: {node_name}.\nError: {e}"
        )
