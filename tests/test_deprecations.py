"""Tests for functionality deprecated for removal in databpy 0.13.0."""

import importlib
import sys

import bpy
import numpy as np
import pytest

import databpy as db
import databpy.material
from databpy._deprecation import REMOVAL_VERSION


def test_removal_version():
    assert REMOVAL_VERSION == "0.13.0"


def test_nodes_is_imported_on_first_use(monkeypatch):
    # run databpy/__init__.py again without the nodes module, restoring both after.
    # This runs in-process, as Blender's bundled Python can't import bpy on its own
    monkeypatch.delitem(sys.modules, "databpy.nodes")
    monkeypatch.delattr(db, "nodes")
    importlib.reload(db)
    assert "databpy.nodes" not in sys.modules

    with pytest.warns(FutureWarning, match="`databpy.nodes` is deprecated") as record:
        nodes = db.nodes
    assert len(record) == 1
    assert record[0].filename == __file__
    assert sys.modules["databpy.nodes"] is nodes


def test_importing_nodes_warns(monkeypatch):
    # import the module again, restoring the original afterwards
    monkeypatch.delitem(sys.modules, "databpy.nodes")
    monkeypatch.delattr(db, "nodes")
    with pytest.warns(FutureWarning, match="`databpy.nodes` is deprecated") as record:
        importlib.import_module("databpy.nodes")
    assert len(record) == 1
    # the warning points at the code importing the module
    assert record[0].filename == __file__
    assert REMOVAL_VERSION in str(record[0].message)


def test_nodes_is_available_from_databpy():
    with pytest.warns(FutureWarning, match="databpy.nodes.new_tree"):
        tree = db.nodes.new_tree("Deprecated")
    assert isinstance(tree, bpy.types.NodeTree)


def test_append_material_from_blend(tmp_path):
    material = bpy.data.materials.new("Deprecated")
    path = str(tmp_path / "materials.blend")
    bpy.data.libraries.write(path, {material})
    bpy.data.materials.remove(material)

    with pytest.warns(
        FutureWarning, match="`databpy.material.append_from_blend` is deprecated"
    ) as record:
        appended = databpy.material.append_from_blend("Deprecated", path)
    assert len(record) == 1
    assert appended.name == "Deprecated"
    assert REMOVAL_VERSION in str(record[0].message)


@pytest.mark.parametrize(
    "call",
    [
        lambda bob: bob.vertices,
        lambda bob: bob.edges,
        lambda bob: db.Attribute(bob.data.attributes["position"]).n_values,
        lambda bob: db.register(),
        lambda bob: db.unregister(),
    ],
    ids=["vertices", "edges", "n_values", "register", "unregister"],
)
def test_removal_version_in_warnings(call):
    bob = db.create_bob(np.random.rand(5, 3))
    with pytest.warns(FutureWarning, match=REMOVAL_VERSION.replace(".", r"\.")):
        call(bob)
