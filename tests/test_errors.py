"""Tests for the exception hierarchy and warnings raised by databpy."""

import warnings

import bpy
import numpy as np
import pytest

import databpy as db


@pytest.fixture
def bob():
    return db.BlenderObject(bpy.data.objects["Cube"])


@pytest.mark.parametrize(
    "call",
    [
        lambda bob: bob["missing"],
        lambda bob: bob.named_attribute("missing"),
        lambda bob: bob.remove_named_attribute("missing"),
        lambda bob: db.AttributeArray(bob.object, "missing"),
        lambda bob: db.GeometrySet(bob.object).named_attribute("missing"),
    ],
)
def test_missing_attribute(bob, call):
    with pytest.raises(db.AttributeNotFoundError, match="missing") as info:
        call(bob)
    # compatible with existing handlers for dictionary-style access and older errors
    assert isinstance(info.value, KeyError)
    assert isinstance(info.value, db.NamedAttributeError)
    assert isinstance(info.value, db.DatabpyError)


def test_error_message_is_not_quoted(bob):
    with pytest.raises(db.AttributeNotFoundError) as info:
        bob["missing"]
    assert str(info.value).startswith("The attribute 'missing'")


def test_mismatch_is_not_a_key_error(bob):
    with pytest.raises(db.NamedAttributeError) as info:
        bob.store_named_attribute(np.zeros(3), "wrong_size")
    assert not isinstance(info.value, KeyError)


def test_remove_required_attribute(bob):
    with pytest.raises(db.NamedAttributeError, match="required"):
        bob.remove_named_attribute("position")


def test_linked_object_error_is_databpy_error(bob):
    bpy.data.objects.remove(bob.object)
    with pytest.raises(db.DatabpyError):
        _ = bob.object


def test_string_warning_points_at_caller(bob):
    with pytest.warns(UserWarning, match="String attributes"):
        bob.store_named_attribute(np.array(list("abcdefgh")), "strings")
    with warnings.catch_warnings(record=True) as record:
        warnings.simplefilter("always")
        bob.named_attribute("strings")
    assert record[0].filename == __file__
