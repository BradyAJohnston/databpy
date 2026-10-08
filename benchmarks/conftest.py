import os
import tempfile

import pytest

# see tests/conftest.py, this has to be set before bpy is first imported
os.environ["BLENDER_USER_EXTENSIONS"] = tempfile.mkdtemp(prefix="databpy-benchmarks-")


@pytest.fixture
def run(benchmark):
    """
    Benchmark a function, starting each round from a fresh file so data-blocks created
    in previous rounds don't affect the timings.
    """
    import bpy

    def _run(func, *args, rounds: int = 10, **kwargs):
        def setup():
            bpy.ops.wm.read_homefile(app_template="")
            return args, kwargs

        return benchmark.pedantic(func, setup=setup, rounds=rounds)

    return _run
