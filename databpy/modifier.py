import bpy

from .object import BlenderObjectBase

POSSIBLE_TYPES = int | float | bool


def _trigger_mesh_update(obj: bpy.types.Object) -> None:
    data = obj.data
    if data is None or not isinstance(data, bpy.types.Mesh):
        raise RuntimeError("Object data is None")

    data.update()
    # we can manually trigger an update of the scene if it is a mesh object
    # by just re-writing the coordinates for a single vertex which properly
    # triggers a refresh of the 3D scene
    try:
        vert = data.vertices[0]  # type: ignore
        vert.co = list(vert.co)  # type: ignore
    except Exception as e:
        print(e)


class NodesModifierInterface(BlenderObjectBase):
    def __init__(self, modifier: bpy.types.NodesModifier):
        super().__init__(modifier.id_data)  # type: ignore
        self._modifier_name = modifier.name

    @property
    def name(self) -> str:
        return self.modifier.name

    @name.setter
    def name(self, value: str) -> None:
        self.modifier.name = value
        self._modifier_name = value

    @property
    def modifier(self) -> bpy.types.NodesModifier:
        mod = self.object.modifiers[self._modifier_name]
        if not isinstance(mod, bpy.types.NodesModifier):
            raise TypeError("Modifier is not a NodesModifier")
        return mod

    @property
    def tree(self) -> bpy.types.NodeTree:
        tree = self.modifier.node_group
        if tree is None:
            raise RuntimeError("Tree not found")
        return tree

    @property
    def tree_interface(self) -> bpy.types.NodeTreeInterface:
        interface = self.tree.interface
        if interface is None:
            raise RuntimeError("Interface not found")
        return interface

    @property
    def input_sockets(self) -> list[bpy.types.NodeTreeInterfaceSocket]:
        return [
            item
            for item in self.tree_interface.items_tree
            if isinstance(item, bpy.types.NodeTreeInterfaceSocket)
            and item.in_out == "INPUT"
        ]

    def get_id_from_name(self, name: str) -> str:
        if not hasattr(self.tree, "interface") or self.tree.interface is None:
            raise RuntimeError("Interface not found")

        for item in self.input_sockets:
            if item.in_out == "INPUT" and item.name == name:
                return item.identifier

        raise RuntimeError(f"Input socket not found: {name=}")

    def get_value(self, name: str) -> POSSIBLE_TYPES:
        return self.modifier[self.get_id_from_name(name)]

    def set_value(self, name: str, value: POSSIBLE_TYPES) -> None:
        self.modifier[self.get_id_from_name(name)] = value
        _trigger_mesh_update(self.object)

    def get_default_attribute(self, name: str) -> str:
        return self.modifier[self.get_id_from_name(name)]

    def list_inputs(self) -> list[str]:
        """Return list of inputs names that can accept and return values"""
        input_names: list[str] = []
        for item in self.input_sockets:
            try:
                self.modifier[item.identifier]
            except KeyError:
                continue
            input_names.append(item.name)

        return input_names

    def _ipython_key_completions_(self) -> list[str]:
        return self.list_inputs()

    def __getitem__(self, name: str) -> POSSIBLE_TYPES:
        return self.get_value(name)

    def __setitem__(self, name: str, value: POSSIBLE_TYPES) -> None:
        self.set_value(name, value)
