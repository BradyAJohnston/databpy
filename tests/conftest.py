import os
import tempfile

import pytest

# Isolate the tests from extensions installed in the user's Blender. `import bpy` adds
# their packages to `sys.path`, where another installed copy of databpy would shadow
# this one. This has to be set before bpy is first imported, which happens when the
# test modules are collected after this file.
os.environ["BLENDER_USER_EXTENSIONS"] = tempfile.mkdtemp(prefix="databpy-tests-")


@pytest.fixture
def g():
    """The `nodebpy.geometry` module, skipping the test before Blender 5.2.

    nodebpy targets Blender 5.2 and fails to import with earlier versions of bpy.
    """
    import bpy

    if bpy.app.version < (5, 2, 0):
        pytest.skip("nodebpy requires Blender 5.2")

    from nodebpy import geometry

    return geometry


@pytest.fixture(autouse=True)
def run_around_tests():
    import bpy

    # Code that will run before each tests

    bpy.ops.wm.read_homefile(app_template="")
    for tree in bpy.data.node_groups:
        bpy.data.node_groups.remove(tree)

    yield

    bpy.ops.wm.read_homefile(app_template="")
    # Code that will run after your test, for example:
    # files_after = # ... do something to check the existing files
    # assert files_before == files_after
