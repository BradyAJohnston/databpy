import bpy


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
