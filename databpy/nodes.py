import bpy
from typing import List, Iterable
import re
import time
import warnings


NODE_DUP_SUFFIX = r"\.\d{3}$"


class NodeGroupCreationError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


def get_output(group):
    return group.nodes[
        bpy.app.translations.pgettext_data(
            "Group Output",
        )
    ]


def get_input(group):
    return group.nodes[
        bpy.app.translations.pgettext_data(
            "Group Input",
        )
    ]


def deduplicate_node_trees(node_trees: List[str]):
    # Compile the regex pattern for matching a suffix of a dot followed by 3 numbers
    node_duplicate_pattern = re.compile(r"\.\d{3}$")
    to_remove: List[bpy.types.GeometryNodeTree] = []

    for node_tree in node_trees:
        # Check if the node tree's name matches the duplicate pattern and is not a "NodeGroup"
        for node in node_tree.nodes:
            if not (
                hasattr(node, "node_tree")
                and node_duplicate_pattern.search(node.node_tree.name)
                and "NodeGroup" not in node.node_tree.name
            ):
                continue

            old_name = node.node_tree.name
            # Remove the numeric suffix to get the original name
            name_sans = old_name.rsplit(".", 1)[0]
            replacement = bpy.data.node_groups.get(name_sans)
            if not replacement:
                continue

            # print(f"matched {old_name} with {name_sans}")
            node.node_tree = replacement
            to_remove.append(bpy.data.node_groups[old_name])

    for tree in to_remove:
        try:
            # remove the data from the blend file
            bpy.data.node_groups.remove(tree)
        except ReferenceError:
            pass


def cleanup_duplicates(purge: bool = False):
    # Collect all node trees from node groups, excluding "NodeGroup" named ones
    node_trees = [tree for tree in bpy.data.node_groups if "NodeGroup" not in tree.name]

    # Call the deduplication function with the collected node trees
    deduplicate_node_trees(node_trees)

    if purge:
        # Purge orphan data blocks from the file
        bpy.ops.outliner.orphans_purge()


class DuplicatePrevention:
    "Context manager to cleanup duplicated node trees when appending node groups"

    def __init__(self, timing=False):
        self.current_names: List[str] = []
        self.start_time = None
        self.timing = timing

    def __enter__(self):
        self.current_names = [tree.name for tree in bpy.data.node_groups]
        if self.timing:
            self.start_time = time.time()

    def __exit__(self, type, value, traceback):
        new_trees = [
            tree for tree in bpy.data.node_groups if tree.name not in self.current_names
        ]
        deduplicate_node_trees(new_trees)
        if self.timing:
            end_time = time.time()
            print(f"De-duplication time: {end_time - self.start_time:.2f} seconds")


class MaintainConnections:
    # capture input and output links, so we can rebuild the links based on name
    # and the sockets they were connected to
    # as we collect them, remove the links so they aren't automatically connected
    # when we change the node_tree for the group

    def __init__(self, node: bpy.types.GeometryNode) -> None:
        self.node = node
        self.input_links = []
        self.output_links = []

    def __enter__(self):
        "Store all the connections in and out of this node for rebuilding on exit."
        self.node_tree = self.node.id_data

        for input in self.node.inputs:
            for input_link in input.links:
                self.input_links.append((input_link.from_socket, input.name))
                self.node_tree.links.remove(input_link)

        for output in self.node.outputs:
            for output_link in output.links:
                self.output_links.append((output.name, output_link.to_socket))
                self.node_tree.links.remove(output_link)

        try:
            self.material = self.node.inputs["Material"].default_value
        except KeyError:
            self.material = None

    def __exit__(self, type, value, traceback):
        "Rebuild the connections in and out of this node that were stored on entry."
        # rebuild the links based on names of the sockets, not their identifiers
        link = self.node_tree.links.new
        for input_link in self.input_links:
            try:
                link(input_link[0], self.node.inputs[input_link[1]])
            except KeyError:
                pass
        for output_link in self.output_links:
            try:
                link(self.node.outputs[output_link[0]], output_link[1])
            except KeyError:
                pass

        # reset all values to tree defaults
        tree = self.node.node_tree
        for item in tree.interface.items_tree:
            if item.item_type == "PANEL":
                continue
            if item.in_out == "INPUT":
                if hasattr(item, "default_value"):
                    self.node.inputs[item.identifier].default_value = item.default_value

        if self.material:
            try:
                self.node.inputs["Material"].default_value = self.material
            except KeyError:
                # the new node doesn't contain a material slot
                pass


def swap_tree(node: bpy.types.GeometryNode, tree: bpy.types.GeometryNodeTree) -> None:
    with MaintainConnections(node):
        node.node_tree = tree
        node.name = tree.name


def append_from_blend(
    name: str, filepath: str, link: bool = False
) -> bpy.types.GeometryNodeTree:
    "Append a Geometry Nodes node tree from the given .blend file"
    try:
        return bpy.data.node_groups[name]
    except KeyError:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            with DuplicatePrevention():
                bpy.ops.wm.append(
                    "EXEC_DEFAULT",
                    directory=filepath,
                    filename=name,
                    link=link,
                    use_recursive=True,
                )
        return bpy.data.node_groups[name]


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
