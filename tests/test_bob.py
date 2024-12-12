import databpy as db
import bpy
import pytest


def test_get_position(snapshot):
    bpy.ops.wm.read_factory_settings()

    att = db.named_attribute(bpy.data.objects["Cube"], "position")
    assert snapshot == att
