import bpy
import pytest
import databpy

databpy.register()


@pytest.fixture(autouse=True)
def run_around_tests():
    # Code that will run before each tests

    bpy.ops.wm.read_homefile(app_template="")
    for tree in bpy.data.node_groups:
        bpy.data.node_groups.remove(tree)

    yield

    bpy.ops.wm.read_homefile(app_template="")
    # Code that will run after your test, for example:
    # files_after = # ... do something to check the existing files
    # assert files_before == files_after
