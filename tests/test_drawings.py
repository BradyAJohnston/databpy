from typing import assert_type

import bpy
import numpy as np
import pytest

import databpy as db
import databpy.array

LINES = np.random.default_rng(0).random((7, 3))
OUTLINE = np.random.default_rng(1).random((5, 3))


@pytest.fixture
def bob() -> db.BlenderObject:
    obj = db.create_grease_pencil_object(
        {"Lines": (LINES, [3, 4]), "Outline": (OUTLINE, [5])}
    )
    return db.BlenderObject(obj)


def _data(bob: db.BlenderObject) -> bpy.types.GreasePencil:
    assert isinstance(bob.data, bpy.types.GreasePencil)
    return bob.data


def _raw(bob: db.BlenderObject, layer: str, name: str, frame: int = 1) -> np.ndarray:
    """Read an attribute straight from a drawing, without going through `Drawing`."""
    keyframe = _data(bob).layers[layer].get_frame_at(frame)
    assert keyframe is not None and keyframe.drawing is not None
    return db.Attribute(keyframe.drawing.attributes[name]).as_array()


def _add_keyframe(bob: db.BlenderObject, layer: str, frame: int, n: int) -> None:
    drawing = _data(bob).layers[layer].frames.new(frame).drawing
    assert drawing is not None
    drawing.add_strokes([n])


def test_drawings_by_layer(bob: db.BlenderObject):
    drawings = bob.drawings
    assert list(drawings) == ["Lines", "Outline"]
    assert len(drawings) == 2
    assert "Lines" in drawings and "Other" not in drawings

    lines = drawings["Lines"]
    assert_type(lines, db.Drawing)
    assert (lines.layer, lines.frame) == ("Lines", 1)
    assert not lines.read_only
    assert [layer for layer, _ in drawings.items()] == ["Lines", "Outline"]

    with pytest.raises(KeyError, match="Other"):
        drawings["Other"]


def test_domain_views(bob: db.BlenderObject):
    lines = bob.drawings["Lines"]
    assert len(lines.point) == 7
    assert len(lines.curve) == 2
    assert "position" in lines.point
    assert "position" not in lines.curve

    position = lines.point["position", db.vec3]
    assert_type(position, db.vec3)
    np.testing.assert_allclose(position, LINES, rtol=1e-6)
    np.testing.assert_allclose(bob.drawings["Outline"]["position"], OUTLINE, rtol=1e-6)


def test_store_and_write_back(bob: db.BlenderObject):
    lines = bob.drawings["Lines"]
    lines.point["w"] = np.arange(7)
    assert "w" in lines.point.list_attributes()
    np.testing.assert_array_equal(_raw(bob, "Lines", "w"), np.arange(7))
    # only stored on that layer's drawing
    assert "w" not in bob.drawings["Outline"]

    w = lines.point["w"]
    w[0] = 10
    w[1:3] += 1
    np.testing.assert_array_equal(_raw(bob, "Lines", "w"), [10, 2, 3, 3, 4, 5, 6])

    # single values are stored on every stroke
    lines.curve["material_index"] = 1
    np.testing.assert_array_equal(_raw(bob, "Lines", "material_index"), [1, 1])

    # new attributes without a domain view go on the POINT domain
    lines["radius"] = 0.5
    np.testing.assert_allclose(_raw(bob, "Lines", "radius"), np.full(7, 0.5))

    with pytest.raises(db.NamedAttributeError, match="POINT"):
        lines.curve["w"] = np.arange(2)
    with pytest.raises(db.NamedAttributeError):
        lines.point["v"] = np.arange(3)


def test_writes_directly(bob: db.BlenderObject, monkeypatch):
    lines = bob.drawings["Lines"]
    lines.point["w"] = np.zeros(7)
    w = lines.point["w"]

    def fail(*args, **kwargs):
        raise AssertionError("the entire attribute was written")

    monkeypatch.setattr(databpy.array, "_store_attribute", fail)
    w[2] = 1
    w[4:] += 2
    np.testing.assert_array_equal(_raw(bob, "Lines", "w"), [0, 0, 1, 0, 2, 2, 2])


def test_srgb(bob: db.BlenderObject):
    lines = bob.drawings["Lines"]
    lines.point["c"] = db.srgb("#FF8000")
    c = lines.point["c", db.srgb]
    np.testing.assert_allclose(c, np.tile([1, 128 / 255, 0, 1], (7, 1)), atol=1e-5)
    c[:, :3] = 0.5
    np.testing.assert_allclose(lines.point["c", db.srgb][:, :3], 0.5, atol=1e-5)


def test_keyframes(bob: db.BlenderObject):
    _add_keyframe(bob, "Lines", 10, 2)

    # the drawing shown at a frame is the one on the last keyframe at or before it
    assert bob.drawings["Lines", 5].frame == 1
    assert bob.drawings["Lines", 10].frame == 10
    assert bob.drawings["Lines", 15].frame == 10
    assert len(bob.drawings["Lines", 10].point) == 2
    with pytest.raises(KeyError, match="frame 0"):
        bob.drawings["Lines", 0]

    db.active_scene().frame_set(10)
    assert bob.drawings["Lines"].frame == 10
    # the Outline layer is still shown on frame 10, from its keyframe on frame 1
    assert bob.drawings["Outline"].frame == 1


def test_arrays_stay_on_their_drawing(bob: db.BlenderObject):
    lines = bob.drawings["Lines"]
    lines.point["w"] = np.zeros(7)
    w = lines.point["w"]

    # neither changing the frame nor adding keyframes, which can move the existing
    # drawings in memory, changes the drawing that is written to
    db.active_scene().frame_set(10)
    _add_keyframe(bob, "Lines", 10, 2)
    _add_keyframe(bob, "Lines", 20, 3)
    w[:] = 1
    np.testing.assert_array_equal(_raw(bob, "Lines", "w", frame=1), np.ones(7))
    assert "w" not in bob.drawings["Lines", 10]
    np.testing.assert_array_equal(lines.point["w"], np.ones(7))


def test_removed_drawing(bob: db.BlenderObject):
    lines = bob.drawings["Lines"]
    w = lines.point["position"]
    data = _data(bob)
    data.layers.remove(data.layers["Lines"])

    with pytest.raises(db.LinkedObjectError, match="Lines"):
        w[0] = 1.0
    with pytest.raises(db.LinkedObjectError, match="Lines"):
        lines.point["position"]
    assert list(bob.drawings) == ["Outline"]


def test_object_points_point_to_drawings(bob: db.BlenderObject):
    with pytest.raises(db.NamedAttributeError, match="bob.drawings"):
        bob["w"] = np.zeros(7)


def test_drawings_need_grease_pencil():
    bob = db.BlenderObject(bpy.data.objects["Cube"])
    with pytest.raises(TypeError, match="GeometrySet"):
        _ = bob.drawings


def test_geometry_set_drawings(bob: db.BlenderObject):
    bob.drawings["Lines"].point["w"] = np.arange(7)
    bob.layer["weight"] = np.array([0.5, 1.0])
    geom = db.GeometrySet(bob.object)

    assert "GREASE_PENCIL" in geom.components()
    assert "GREASE_PENCIL: 2 layers" in repr(geom)
    np.testing.assert_allclose(
        geom.named_attribute("weight", component="GREASE_PENCIL"), [0.5, 1.0]
    )
    np.testing.assert_allclose(geom.named_attribute("weight"), [0.5, 1.0])

    lines = geom.drawings["Lines"]
    assert lines.read_only
    w = lines.point["w", db.int32]
    assert_type(w, db.int32)
    np.testing.assert_array_equal(w, np.arange(7))
    # a copy of evaluated geometry, so changes aren't written anywhere
    assert w._link is None
    w[0] = 10
    with pytest.raises(TypeError, match="read-only"):
        lines.point["w"] = np.zeros(7)


def test_geometry_set_without_grease_pencil():
    geom = db.GeometrySet(bpy.data.objects["Cube"])
    assert "GREASE_PENCIL" not in geom.components()
    assert len(geom.drawings) == 0
    with pytest.raises(KeyError):
        geom.drawings["Layer"]


def test_geometry_set_drawings_from_geometry_nodes(g):
    # grease pencil that only exists in the evaluated geometry of a curves object
    positions = np.random.default_rng(2).random((6, 3))
    obj = db.create_curves_object(positions, [3, 3])
    with g.tree("to_gp") as tree:
        g.CurvesToGreasePencil(tree.inputs.geometry(), instances_as_layers=False) >> (
            tree.outputs.geometry()
        )
    modifier = obj.modifiers.new("to_gp", "NODES")
    assert isinstance(modifier, bpy.types.NodesModifier)
    modifier.node_group = tree.tree

    geom = db.GeometrySet(obj)
    assert list(geom.components()) == ["GREASE_PENCIL"]
    (layer,) = geom.drawings
    drawing = geom.drawings[layer]
    assert len(drawing.curve) == 2
    np.testing.assert_allclose(drawing.point["position"], positions, rtol=1e-6)
