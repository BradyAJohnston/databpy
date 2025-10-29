import bpy
import pytest
import databpy
from pathlib import Path
from syrupy.extensions.amber import AmberSnapshotExtension

databpy.register()


def get_bpy_version():
    """Get the major.minor version of bpy"""
    return f"{bpy.app.version[0]}.{bpy.app.version[1]}"


class BpyVersionExtension(AmberSnapshotExtension):
    """Custom extension that uses version-specific snapshot directories"""

    @classmethod
    def dirname(cls, *, test_location) -> str:
        """Override dirname to include bpy version in path"""
        version = get_bpy_version()
        test_dir = Path(test_location.filepath).parent
        return str(test_dir / "__snapshots__" / f"bpy_{version}")


@pytest.fixture
def snapshot(snapshot):
    """Override snapshot fixture to use version-specific directory"""
    return snapshot.use_extension(BpyVersionExtension)


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
