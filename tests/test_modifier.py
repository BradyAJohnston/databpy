import bpy

import databpy as db


def test_modifier():
    cube = bpy.data.objects["Cube"]
    tree = db.nodes.new_tree()
    tree.interface.new_socket(  # type: ignore
        name="Count", in_out="INPUT", socket_type="NodeSocketInt"
    ).default_value = 3
    mod = db.NodesModifierInterface(cube.modifiers.new("GeometryNodes", "NODES"))  # type: ignore
    mod.tree = tree

    assert mod["Count"] == 3
    mod["Count"] = 4
    assert mod["Count"] == 4
