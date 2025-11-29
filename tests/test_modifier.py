import bpy
import pytest

import databpy as db


def test_modifier():
    cube = bpy.data.objects["Cube"]
    modifier = cube.modifiers.new("GeometryNodes", "NODES")
    assert isinstance(modifier, bpy.types.NodesModifier)
    tree = db.nodes.new_tree()
    tree.interface.new_socket(  # type: ignore
        name="Count", in_out="INPUT", socket_type="NodeSocketInt"
    ).default_value = 3
    mod = db.NodesModifierInterface(modifier)
    with pytest.raises(RuntimeError):
        mod.tree
    mod.tree = tree
    assert mod.name == "GeometryNodes"
    mod.name = "New Name"
    assert mod.name == "New Name"

    assert mod["Count"] == 3
    mod["Count"] = 4
    assert mod["Count"] == 4

    assert mod.list_inputs() == ["Count"]
    assert mod.list_inputs() == mod._ipython_key_completions_()
    assert mod.list_inputs() == dir(mod)

    assert mod._key_use_att == "Socket_1_use_attribute"
    assert mod._key_attr_name == "Socket_1_attribute_name"

    assert mod.get_attr_name("Count") == "Something"

    with pytest.raises(ValueError):
        mod.get_id_from_name("non_existant_input")

    wrong_mod = cube.modifiers.new(name="test", type="NORMAL_EDIT")

    with pytest.raises(AssertionError):
        db.NodesModifierInterface(wrong_mod)  # type: ignore
