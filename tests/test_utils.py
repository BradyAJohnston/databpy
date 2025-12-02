import numpy as np
import pytest
from pathlib import Path
import databpy.utils as utils


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
    with pytest.raises(ValueError):
        utils.path_resolve(123)
