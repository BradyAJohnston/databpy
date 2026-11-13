from typing import assert_type

import bpy
import numpy as np
import pytest

import databpy as db
from databpy.array import _linear_to_srgb, _srgb_to_linear


@pytest.fixture
def bob():
    bpy.ops.wm.read_factory_settings()
    return db.BlenderObject(bpy.data.objects["Cube"])


def _blender_srgb(bob: db.BlenderObject, name: str) -> np.ndarray:
    """Read a color attribute through Blender's own sRGB conversion."""
    attribute = bob.attributes[name]
    values = np.empty(len(attribute.data) * 4, dtype=np.float32)
    attribute.data.foreach_get("color_srgb", values)
    return values.reshape(-1, 4)


def _blender_linear(bob: db.BlenderObject, name: str) -> np.ndarray:
    attribute = bob.attributes[name]
    values = np.empty(len(attribute.data) * 4, dtype=np.float32)
    attribute.data.foreach_get("color", values)
    return values.reshape(-1, 4)


SRGB = np.random.default_rng(0).random((8, 4), dtype=np.float32)
# Blender approximates the sRGB curve, which is up to ~1e-4 from the exact curve
BLENDER_ATOL = 3e-4


def test_conversion():
    np.testing.assert_allclose(
        _linear_to_srgb(np.array([[0.5, 0.0, 1.0, 0.5]])),
        [[0.7354, 0.0, 1.0, 0.5]],
        atol=1e-4,
    )
    values = np.array([[-0.5, 0.001, 0.5, 0.25], [2.0, 0.04, 1.0, 1.0]])
    np.testing.assert_allclose(
        _srgb_to_linear(_linear_to_srgb(values)), values, atol=1e-6
    )
    # alpha is left as it is
    np.testing.assert_array_equal(_srgb_to_linear(values)[:, 3], values[:, 3])


def test_wrap_doesnt_convert_or_copy():
    v = db.srgb(SRGB)
    assert_type(v, db.srgb)
    assert np.shares_memory(v, SRGB)
    assert v.atype == db.AttributeTypes.FLOAT_COLOR


def test_store_converts_to_linear(bob: db.BlenderObject):
    bob.point["c"] = db.srgb(SRGB)
    assert db.Attribute(bob.attributes["c"]).atype == db.AttributeTypes.FLOAT_COLOR
    # matches Blender's own conversion
    np.testing.assert_allclose(_blender_srgb(bob, "c"), SRGB, atol=BLENDER_ATOL)
    np.testing.assert_allclose(_blender_linear(bob, "c"), _srgb_to_linear(SRGB))
    # the wrapped array isn't changed by storing it
    np.testing.assert_array_equal(db.srgb(SRGB), SRGB)


def test_read_converts_to_srgb(bob: db.BlenderObject):
    bob.point["c"] = db.color(_srgb_to_linear(SRGB))
    c = bob.point["c", db.srgb]
    assert_type(c, db.srgb)
    assert type(c) is db.srgb
    np.testing.assert_allclose(c, SRGB, atol=1e-5)

    # a plain read is still the linear values
    assert type(bob["c"]) is db.color
    np.testing.assert_allclose(bob["c"], _srgb_to_linear(SRGB))

    values = db.named_attribute(bob.object, "c", atype=db.srgb)
    assert_type(values, db.srgb)
    np.testing.assert_allclose(values, SRGB, atol=1e-5)
    assert values._link is None


def test_changes_are_written_back_as_linear(bob: db.BlenderObject):
    bob.point["c"] = db.srgb(SRGB)
    c = bob.point["c", db.srgb]

    c[:, :3] *= 0.5
    np.testing.assert_allclose(
        _blender_srgb(bob, "c")[:, :3], SRGB[:, :3] * 0.5, atol=BLENDER_ATOL
    )

    # views that only hold some channels are converted by their channel
    c[:, 0] = 0.2
    c[:, 3] = 0.3
    linear = _blender_linear(bob, "c")
    np.testing.assert_allclose(
        linear[:, 0], _srgb_to_linear(np.array([[0.2, 0, 0, 0]]))[0, 0]
    )
    np.testing.assert_allclose(linear[:, 3], 0.3)

    c[2] = [1.0, 1.0, 1.0, 1.0]
    np.testing.assert_allclose(_blender_linear(bob, "c")[2], 1.0, atol=1e-6)


def test_written_back_after_the_attribute_is_removed(bob: db.BlenderObject):
    bob.point["c"] = db.srgb(SRGB)
    c = bob.point["c", db.srgb]
    bob.remove_named_attribute("c")
    c[0] = 0.5  # re-creates the attribute
    np.testing.assert_allclose(_blender_srgb(bob, "c")[0], 0.5, atol=BLENDER_ATOL)


def test_math_keeps_srgb(bob: db.BlenderObject):
    bob.point["c"] = db.srgb(SRGB)
    c = bob.point["c", db.srgb]

    darker = c * 0.5
    assert type(darker) is db.srgb
    assert darker._link is None
    bob.point["d"] = darker
    np.testing.assert_allclose(_blender_srgb(bob, "d"), SRGB * 0.5, atol=BLENDER_ATOL)

    # comparisons and reductions aren't colors
    assert type(c > 0.5) is np.ndarray
    assert type(c.sum(axis=0)) is np.ndarray


def test_mismatched_type_raises(bob: db.BlenderObject):
    with pytest.raises(db.NamedAttributeError, match="FLOAT_VECTOR"):
        bob.point["position", db.srgb]
    bob.point["q"] = db.quat(np.ones((8, 4)))
    with pytest.raises(db.NamedAttributeError):
        bob.point["q"] = db.srgb(SRGB)


def test_geometry_set_reads_srgb(bob: db.BlenderObject):
    bob.point["c"] = db.srgb(SRGB)
    geom = db.GeometrySet(bob.object)
    values = geom.named_attribute("c", atype=db.srgb)
    assert type(values) is db.srgb
    np.testing.assert_allclose(values, SRGB, atol=1e-5)


@pytest.mark.parametrize(
    "code, rgba",
    [
        ("#FF8000", [255, 128, 0, 255]),
        ("ff8000", [255, 128, 0, 255]),
        ("#FF800080", [255, 128, 0, 128]),
        ("#f80", [255, 136, 0, 255]),
        ("#f808", [255, 136, 0, 136]),
    ],
)
def test_hex_codes(code, rgba):
    np.testing.assert_allclose(db.srgb(code), np.array(rgba) / 255)
    np.testing.assert_array_equal(db.color8(code), rgba)


def test_hex_code_lists():
    colors = db.srgb(["#FF0000", "#00FF00", "#0000FF80"])
    assert colors.shape == (3, 4)
    np.testing.assert_allclose(colors[2], [0, 0, 1, 128 / 255])
    assert db.color8(np.array(["#000", "#fff"])).dtype == np.uint8


@pytest.mark.parametrize("code", ["#FF800", "#GG8000", "#FF80001", ""])
def test_invalid_hex_codes_raise(code):
    with pytest.raises(ValueError, match="hex color code"):
        db.srgb(code)


def test_store_hex_codes(bob: db.BlenderObject):
    bob.point["c"] = db.srgb("#FF8000")
    np.testing.assert_allclose(
        _blender_srgb(bob, "c"),
        np.tile([1, 128 / 255, 0, 1], (8, 1)),
        atol=BLENDER_ATOL,
    )
    bob.face["b"] = db.color8(["#FF8000"] * 6)
    np.testing.assert_array_equal(
        bob.face["b", db.color8], np.tile([255, 128, 0, 255], (6, 1))
    )
