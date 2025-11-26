import bpy
from .object import BlenderObjectBase


VALUE_TYPES = int | float | bool


class GeometryNodesModifier(BlenderObjectBase):
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
    def modifier(self) -> bpy.types.Modifier:
        return self.object.modifiers[self._modifier_name]

    @property
    def tree(self) -> bpy.types.GeometryNodeTree:
        return self.modifier.node_group  # type: ignore

    def get_id_from_name(self, name: str) -> str:
        if not hasattr(self.tree, "interface"):
            raise RuntimeError
        if not hasattr(self.tree.interface, "items_tree"):
            raise RuntimeError
        item = self.tree.interface.items_tree.get(name)
        if not isinstance(item, bpy.types.NodeTreeInterfaceItem):
            raise RuntimeError
        return item.identifier  # type: ignore

    def get_value(self, name: str) -> VALUE_TYPES:
        return self.modifier[self.get_id_from_name(name)]

    def set_value(self, name: str, value: VALUE_TYPES) -> None:
        self.modifier[self.get_id_from_name(name)] = value
        # we can manually trigger an update of the scene if it is a mesh object
        # by just re-writing the coordinates for a single vertex which properly
        # triggers a refresh of the 3D scene
        if hasattr(self.object.data, "vertices"):
            try:
                self.object.data.vertices[0].co = self.object.data.vertices[0].co  # type: ignore
            except Exception as e:
                print(e)

    def list_inputs(self) -> list[str]:
        """Return list of inputs that can accept and return values"""
        possible_inputs: list[str] = []
        for item in self.tree.interface.items_tree:  # type: ignore
            if item.in_out != "INPUT":  # type: ignore
                continue
            try:
                self.modifier[item.identifier]  # type: ignore
            except KeyError:
                continue

            possible_inputs.append(item.name)  # type: ignore

        return possible_inputs

    def _ipython_key_completions_(self) -> list[str]:
        return self.list_inputs()

    def __getitem__(self, name: str) -> VALUE_TYPES:
        if not isinstance(name, str):
            raise ValueError("Input name must be a string")
        return self.get_value(name)

    def __setitem__(self, name: str, value: VALUE_TYPES) -> None:
        self.set_value(name, value)
