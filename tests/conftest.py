import bpy
import pytest


@pytest.fixture
def default_scene(empty: bool = False) -> None:
    bpy.ops.wm.read_factory_settings(use_empty=empty)
