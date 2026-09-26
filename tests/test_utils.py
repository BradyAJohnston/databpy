from pathlib import Path
from typing import Any

import bpy
import numpy as np
import pytest

from databpy import utils


def test_centre_unweighted():
    positions = np.array([[0, 0, 0], [2, 2, 2]])
    result = utils.centre(positions)
    np.testing.assert_array_equal(result, np.array([1, 1, 1]))


def test_centre_weighted():
    positions = np.array([[0, 0, 0], [2, 2, 2]])
    weights = np.array([1, 3])
    result = utils.centre(positions, weights)
    np.testing.assert_array_equal(result, np.array([1.5, 1.5, 1.5]))


def test_lerp_scalar():
    result = utils.lerp(0, 10, 0.5)
    assert result == 5.0


def test_lerp_array():
    a = np.array([0, 0, 0])
    b = np.array([10, 10, 10])
    result = utils.lerp(a, b, 0.5)
    np.testing.assert_array_equal(result, np.array([5, 5, 5]))


def test_lerp_extremes():
    a = np.array([1, 1, 1])
    b = np.array([2, 2, 2])
    result_zero = utils.lerp(a, b, 0.0)
    result_one = utils.lerp(a, b, 1.0)
    np.testing.assert_array_equal(result_zero, a)
    np.testing.assert_array_equal(result_one, b)


def test_path_resolve_str():
    result = utils.path_resolve("//test.blend")
    assert isinstance(result, Path)
    assert result.is_absolute()


def test_path_resolve_path():
    input_path = Path("//test.blend")
    result = utils.path_resolve(input_path)
    assert isinstance(result, Path)
    assert result.is_absolute()


def test_path_resolve_invalid():
    not_a_path: Any = 123
    with pytest.raises(TypeError):
        utils.path_resolve(not_a_path)


def test_require():
    assert utils.require(5) == 5
    assert utils.require("value") == "value"
    with pytest.raises(ValueError, match="got None"):
        utils.require(None)
    with pytest.raises(ValueError, match="custom message"):
        utils.require(None, "custom message")


def test_require_data():
    cube = bpy.data.objects["Cube"]
    camera = bpy.data.objects["Camera"]

    assert utils.mesh_data(cube) == cube.data
    assert utils.require_data(cube, bpy.types.Mesh) == cube.data

    with pytest.raises(TypeError, match="expected Mesh"):
        utils.mesh_data(camera)
    with pytest.raises(TypeError, match="expected Curves"):
        utils.curves_data(cube)
    with pytest.raises(TypeError, match="expected PointCloud"):
        utils.pointcloud_data(cube)
    with pytest.raises(TypeError, match="expected Volume"):
        utils.volume_data(cube)


def test_active_scene():
    scene = utils.active_scene()
    assert isinstance(scene, bpy.types.Scene)
    assert scene == bpy.context.scene


def test_active_object():
    view_layer = utils.require(bpy.context.view_layer)
    view_layer.objects.active = bpy.data.objects["Cube"]
    assert utils.active_object().name == "Cube"

    view_layer.objects.active = None
    with pytest.raises(ValueError, match="No active object"):
        utils.active_object()
