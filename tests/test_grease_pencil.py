from typing import assert_type

import bpy
import numpy as np
import pytest

import databpy as db


@pytest.fixture
def gp_obj() -> bpy.types.Object:
    return db.create_grease_pencil_object(
        {
            "Lines": (np.random.default_rng(0).random((7, 3)), [3, 4]),
            "Outline": (np.random.default_rng(1).random((5, 3)), [5]),
        }
    )


def _data(obj: bpy.types.Object) -> bpy.types.GreasePencil:
    assert isinstance(obj.data, bpy.types.GreasePencil)
    return obj.data


def _drawing(obj: bpy.types.Object, layer: str) -> bpy.types.GreasePencilDrawing:
    frame = _data(obj).layers[layer].current_frame()
    assert frame is not None and frame.drawing is not None
    return frame.drawing


def test_create_grease_pencil_object(gp_obj: bpy.types.Object):
    assert [layer.name for layer in _data(gp_obj).layers] == ["Lines", "Outline"]

    lines = _drawing(gp_obj, "Lines")
    assert [len(stroke.points) for stroke in lines.strokes] == [3, 4]
    np.testing.assert_allclose(
        db.Attribute(lines.attributes["position"]).as_array(),
        np.random.default_rng(0).random((7, 3)),
        rtol=1e-6,
    )
    assert [len(s.points) for s in _drawing(gp_obj, "Outline").strokes] == [5]


def test_create_grease_pencil_object_empty():
    obj = db.create_grease_pencil_object()
    assert len(_data(obj).layers) == 0


def test_create_grease_pencil_object_mismatched_sizes():
    with pytest.raises(ValueError, match="Lines"):
        db.create_grease_pencil_object({"Lines": (np.zeros((4, 3)), [3, 2])})


def test_create_grease_pencil_object_empty_layer():
    # Blender crashes when adding an empty list of strokes
    obj = db.create_grease_pencil_object(
        {"Empty": (np.empty((0, 3)), []), "Lines": (np.zeros((3, 3)), [3])}
    )
    assert [layer.name for layer in _data(obj).layers] == ["Empty", "Lines"]
    assert len(_drawing(obj, "Empty").strokes) == 0
    assert len(_drawing(obj, "Lines").strokes) == 1


@pytest.mark.parametrize(
    "layers",
    [
        # the first layer is valid, so it would be created before the error
        {"A": (np.zeros((3, 3)), [3]), "B": (np.zeros((4, 3)), [3, 2])},
        {"A": (np.zeros((4, 2)), [4])},
        {"A": (np.zeros((3, 3)), [3, 0])},
        {"A": (np.zeros((3, 3)), [4, -1])},
        {"A": (np.zeros((4, 3)), [[2, 2]])},
        {"A": (np.zeros((3, 3)), [1.5, 1.5])},
        # Blender renames an empty layer name, which is only seen after creating it
        {"A": (np.zeros((3, 3)), [3]), "": (np.zeros((3, 3)), [3])},
    ],
)
def test_create_grease_pencil_object_invalid_leaves_nothing(layers):
    objects = set(bpy.data.objects)
    grease_pencils = set(bpy.data.grease_pencils)
    with pytest.raises(ValueError):
        db.create_grease_pencil_object(layers)
    assert set(bpy.data.objects) == objects
    assert set(bpy.data.grease_pencils) == grease_pencils


def test_create_grease_pencil_object_on_current_frame():
    scene = bpy.context.scene
    assert scene is not None
    previous = scene.frame_current
    scene.frame_set(10)
    try:
        obj = db.create_grease_pencil_object({"L": (np.zeros((2, 3)), [2])})
        layer = _data(obj).layers["L"]
        assert [frame.frame_number for frame in layer.frames] == [10]
        scene.frame_set(1)
        # the drawing is only shown from the frame it was created on
        assert layer.current_frame() is None
    finally:
        scene.frame_set(previous)


def test_from_grease_pencil():
    bob = db.BlenderObject.from_grease_pencil(
        {"Lines": (np.zeros((7, 3)), [3, 4])}, name="GP"
    )
    assert isinstance(bob.data, bpy.types.GreasePencil)
    assert bob.name.startswith("GP")
    with pytest.raises(TypeError, match="LAYER"):
        len(bob)
    # a truth test doesn't fall back to the length
    assert bob


def test_points_and_strokes_are_not_on_the_object(gp_obj: bpy.types.Object):
    # the points and strokes are on each layer's drawing, so the object's own
    # attributes only hold the LAYER domain
    data = _data(gp_obj)
    assert data.attributes.domain_size("POINT") == 0
    assert data.attributes.domain_size("CURVE") == 0
    assert data.attributes.domain_size("LAYER") == 2
    assert "position" not in db.list_attributes(gp_obj)

    for domain in ["POINT", "CURVE"]:
        with pytest.raises(db.NamedAttributeError, match=f'domain="LAYER".*{domain}'):
            db.store_named_attribute(gp_obj, np.zeros(12), "x", domain=domain)
    with pytest.raises(db.NamedAttributeError, match='domain="LAYER"'):
        db.store_named_attribute(gp_obj, np.zeros(2), "x")
    assert "x" not in db.list_attributes(gp_obj)


def test_layer_attributes(gp_obj: bpy.types.Object):
    bob = db.BlenderObject(gp_obj)
    bob.store_named_attribute(np.array([0.5, 1.0]), "weight", domain="LAYER")
    assert bob.list_attributes() == ["weight"]
    np.testing.assert_allclose(bob["weight"], [0.5, 1.0])

    # changes are written back to Blender
    weight = bob["weight"]
    weight[1] = 2.0
    np.testing.assert_allclose(db.named_attribute(gp_obj, "weight"), [0.5, 2.0])

    with pytest.raises(db.NamedAttributeError, match="domain `LAYER` with 2 elements"):
        bob["weight"] = np.zeros(3)

    bob.remove_named_attribute("weight")
    assert bob.list_attributes() == []


def test_new_attributes_need_a_domain(gp_obj: bpy.types.Object):
    # without a domain, a new attribute would be stored per layer when per point
    # was likely meant, so it raises instead
    bob = db.BlenderObject(gp_obj)
    with pytest.raises(db.NamedAttributeError):
        bob["id"] = np.array([1, 2])
    with pytest.raises(db.NamedAttributeError):
        db.store_named_attribute(gp_obj, np.array([1, 2]), "id")
    assert "id" not in bob.list_attributes()

    bob.store_named_attribute(np.array([1, 2]), "id", domain="LAYER")
    attribute = db.Attribute(_data(gp_obj).attributes["id"])
    assert attribute.domain == db.AttributeDomains.LAYER
    assert attribute.atype == db.AttributeTypes.INT
    # existing attributes keep their domain, so no domain is needed to overwrite
    bob["id"] = np.array([3, 4])
    np.testing.assert_array_equal(bob["id"], [3, 4])


def test_layer_attributes_created_by_blender(gp_obj: bpy.types.Object):
    # attributes that databpy didn't create can still be read and written
    _data(gp_obj).attributes.new("tint", "FLOAT_COLOR", "LAYER")
    bob = db.BlenderObject(gp_obj)
    assert bob["tint"].shape == (2, 4)
    bob["tint"] = np.ones((2, 4))
    np.testing.assert_allclose(bob["tint"], 1)


def test_layer_view(gp_obj: bpy.types.Object):
    bob = db.BlenderObject(gp_obj)
    assert len(bob.layer) == 2
    # the points and strokes aren't on the object, so these views are empty
    assert len(bob.point) == 0
    assert len(bob.curve) == 0
    assert bob.point.list_attributes() == []

    bob.layer["weight"] = db.float32(np.array([0.5, 1.0]))
    assert "weight" in bob.layer
    assert bob.layer.list_attributes() == ["weight"]

    weight = bob.layer["weight", db.float32]
    assert_type(weight, db.float32)
    weight[1] = 2.0
    np.testing.assert_allclose(db.named_attribute(gp_obj, "weight"), [0.5, 2.0])

    with pytest.raises(db.NamedAttributeError, match="FLOAT"):
        bob.layer["weight", db.vec3]
    with pytest.raises(db.NamedAttributeError, match="POINT"):
        bob.point["x"] = np.zeros(12)


def test_layer_view_reads_typed_arrays(gp_obj: bpy.types.Object):
    bob = db.BlenderObject(gp_obj)
    bob["id"] = np.array([1, 2])
    assert type(bob.layer["id"]) is db.int32

    _data(gp_obj).attributes.new("tint", "FLOAT_COLOR", "LAYER")
    assert bob.layer["tint", db.color].shape == (2, 4)
    bob.layer["tint"] = db.color(np.ones((2, 4)))
    np.testing.assert_allclose(bob.layer["tint"], 1)
