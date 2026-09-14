from typing import Literal, cast

import bpy

NODE_DUP_SUFFIX = r"\.\d{3}$"

# only some socket subclasses carry a `default_value`, and each declares its own
# value type, so generic access has to happen dynamically through this name
_DEFAULT_VALUE_ATTR = "default_value"


class NodeGroupCreationError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


def get_output(group: bpy.types.NodeTree) -> bpy.types.Node:
    return group.nodes[
        bpy.app.translations.pgettext_data(
            "Group Output",
        )
    ]


def get_input(group: bpy.types.NodeTree) -> bpy.types.Node:
    return group.nodes[
        bpy.app.translations.pgettext_data(
            "Group Input",
        )
    ]


def tree_interface(tree: bpy.types.NodeTree) -> bpy.types.NodeTreeInterface:
    """Return the interface of a node tree, raising an error if it has none.

    `NodeTree.interface` is typed as optional in the Blender API, but a valid
    node group always has one, so this narrows the type for further use.
    """
    interface = tree.interface
    if interface is None:
        raise NodeGroupCreationError(f"Node tree '{tree.name}' has no interface")
    return interface


def new_socket(
    tree: bpy.types.NodeTree,
    name: str,
    in_out: Literal["INPUT", "OUTPUT"] = "INPUT",
    socket_type: str = "NodeSocketGeometry",
) -> bpy.types.NodeTreeInterfaceSocket:
    """Create a new input or output socket on the interface of the node tree.

    Parameters
    ----------
    tree : bpy.types.NodeTree
        The node tree to add the socket to.
    name : str
        The name of the new socket.
    in_out : Literal["INPUT", "OUTPUT"], optional
        Whether the socket is an input or an output. Defaults to "INPUT".
    socket_type : str, optional
        The socket idname, e.g. "NodeSocketFloat". Defaults to
        "NodeSocketGeometry".

    Returns
    -------
    bpy.types.NodeTreeInterfaceSocket
        The newly created socket.
    """
    # Blender accepts any socket idname for `socket_type` at runtime, but the
    # published type information only declares the "DEFAULT" enum value, so the
    # value is cast to match
    return tree_interface(tree).new_socket(
        name,
        in_out=in_out,
        socket_type=cast(Literal["DEFAULT"], socket_type),
    )


def input_socket(node: bpy.types.Node, key: int | str) -> bpy.types.NodeSocket:
    """Get an input socket of a node by index or name."""
    return node.inputs[key]


def output_socket(node: bpy.types.Node, key: int | str) -> bpy.types.NodeSocket:
    """Get an output socket of a node by index or name."""
    return node.outputs[key]


def socket_value(socket: bpy.types.NodeSocket) -> object:
    """Return the default value of a socket.

    Raises
    ------
    TypeError
        If this type of socket has no default value (e.g. a Geometry socket).
    """
    if not hasattr(socket, "default_value"):
        raise TypeError(f"Socket '{socket.name}' has no default value")
    return socket.default_value


def set_socket_value(socket: bpy.types.NodeSocket, value: object) -> None:
    """Set the default value of a socket.

    Raises
    ------
    TypeError
        If this type of socket has no default value (e.g. a Geometry socket),
        or the value is incompatible with the socket type.
    """
    if not hasattr(socket, _DEFAULT_VALUE_ATTR):
        raise TypeError(f"Socket '{socket.name}' has no default value")
    setattr(socket, _DEFAULT_VALUE_ATTR, value)


class MaintainConnections:
    # capture input and output links, so we can rebuild the links based on name
    # and the sockets they were connected to
    # as we collect them, remove the links so they aren't automatically connected
    # when we change the node_tree for the group

    node_tree: bpy.types.NodeTree

    def __init__(self, node: bpy.types.Node) -> None:
        if not isinstance(node, bpy.types.GeometryNodeGroup):
            raise TypeError(
                f"MaintainConnections requires a GeometryNodeGroup, "
                f"not {type(node).__name__}"
            )
        self.node = node
        self.input_links: list[tuple[bpy.types.NodeSocket, str]] = []
        self.output_links: list[tuple[str, bpy.types.NodeSocket]] = []
        self.material: object = None

    def __enter__(self):
        "Store all the connections in and out of this node for rebuilding on exit."
        tree = self.node.id_data
        if not isinstance(tree, bpy.types.NodeTree):
            raise TypeError(f"Node '{self.node.name}' is not part of a node tree")
        self.node_tree = tree

        for node_input in self.node.inputs:
            for input_link in node_input.links or ():
                from_socket = input_link.from_socket
                if from_socket is not None:
                    self.input_links.append((from_socket, node_input.name))
                self.node_tree.links.remove(input_link)

        for node_output in self.node.outputs:
            for output_link in node_output.links or ():
                to_socket = output_link.to_socket
                if to_socket is not None:
                    self.output_links.append((node_output.name, to_socket))
                self.node_tree.links.remove(output_link)

        try:
            self.material = socket_value(self.node.inputs["Material"])
        except (KeyError, TypeError):
            self.material = None

    def __exit__(self, type, value, traceback):
        "Rebuild the connections in and out of this node that were stored on entry."
        # rebuild the links based on names of the sockets, not their identifiers
        link = self.node_tree.links.new
        for from_socket, input_name in self.input_links:
            try:
                link(from_socket, self.node.inputs[input_name])
            except KeyError:
                pass
        for output_name, to_socket in self.output_links:
            try:
                link(self.node.outputs[output_name], to_socket)
            except KeyError:
                pass

        # reset all values to tree defaults
        tree = self.node.node_tree
        if tree is not None:
            for item in tree_interface(tree).items_tree:
                # panels and other non-socket items don't carry values
                if not isinstance(item, bpy.types.NodeTreeInterfaceSocket):
                    continue
                if item.in_out == "INPUT" and hasattr(item, "default_value"):
                    try:
                        set_socket_value(
                            self.node.inputs[item.identifier], item.default_value
                        )
                    except (KeyError, TypeError):
                        pass

        if self.material is not None:
            try:
                set_socket_value(self.node.inputs["Material"], self.material)
            except (KeyError, TypeError):
                # the new node doesn't contain a material slot
                pass
