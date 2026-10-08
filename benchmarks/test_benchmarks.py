"""
Benchmarks for creating geometry and reading / writing attributes.

Run locally with `uv run pytest benchmarks --codspeed`, which reports wall-clock times.
In CI they run under CodSpeed's CPU simulation, which tracks results over time and
reports changes on pull requests.
"""

import bpy
import numpy as np
import pytest

import databpy as db

N = 100_000
GRID = 300  # GRID * GRID vertices and (GRID - 1) ** 2 quads

rng = np.random.default_rng(0)
POSITIONS = rng.random((N, 3), dtype=np.float32)
EDGES = np.stack([np.arange(N - 1), np.arange(1, N)], axis=1)


def _grid():
    x, y = np.meshgrid(np.arange(GRID), np.arange(GRID))
    vertices = np.stack([x.ravel(), y.ravel(), np.zeros(x.size)], axis=1)
    i = (y[:-1, :-1] * GRID + x[:-1, :-1]).ravel()
    faces = np.stack([i, i + 1, i + GRID + 1, i + GRID], axis=1)
    return vertices, faces


GRID_VERTICES, GRID_FACES = _grid()
# split each quad into a triangle and a quad, so faces have mixed sizes
RAGGED_FACES = [f for q in GRID_FACES.tolist() for f in (q[:3], q)]


@pytest.mark.benchmark(group="mesh-vertices")
def test_from_pydata_vertices(run):
    # Blender's own constructor, as a reference point
    run(lambda: bpy.data.meshes.new("Mesh").from_pydata(POSITIONS, [], []))


@pytest.mark.benchmark(group="mesh-vertices")
def test_create_mesh_vertices(run):
    run(db.create_mesh_object, POSITIONS)


@pytest.mark.benchmark(group="mesh-edges")
def test_from_pydata_edges(run):
    run(lambda: bpy.data.meshes.new("Mesh").from_pydata(POSITIONS, EDGES, []))


@pytest.mark.benchmark(group="mesh-edges")
def test_create_mesh_edges(run):
    run(db.create_mesh_object, POSITIONS, EDGES)


@pytest.mark.benchmark(group="mesh-faces")
def test_from_pydata_faces(run):
    run(lambda: bpy.data.meshes.new("Mesh").from_pydata(GRID_VERTICES, [], GRID_FACES))


@pytest.mark.benchmark(group="mesh-faces")
def test_create_mesh_faces(run):
    run(db.create_mesh_object, GRID_VERTICES, faces=GRID_FACES)


@pytest.mark.benchmark(group="mesh-faces")
def test_create_mesh_ragged_faces(run):
    run(db.create_mesh_object, GRID_VERTICES, faces=RAGGED_FACES)


@pytest.mark.benchmark(group="mesh-faces")
def test_new_from_pydata_faces(run):
    def func():
        db.create_bob().new_from_pydata(GRID_VERTICES, faces=GRID_FACES)

    run(func)


@pytest.mark.benchmark(group="pointcloud")
def test_create_pointcloud(run):
    run(db.create_pointcloud_object, POSITIONS)


@pytest.mark.benchmark(group="curves")
def test_create_curves(run):
    run(db.create_curves_object, POSITIONS, np.full(N // 10, 10))


@pytest.mark.benchmark(group="attributes")
def test_store_named_attribute(benchmark):
    obj = db.create_pointcloud_object(POSITIONS)
    values = rng.random(N)
    benchmark(db.store_named_attribute, obj, values, "value")


@pytest.mark.benchmark(group="attributes")
def test_named_attribute(benchmark):
    obj = db.create_pointcloud_object(POSITIONS)
    benchmark(db.named_attribute, obj, "position")


def _attribute_values(atype: db.AttributeTypes, n: int) -> np.ndarray:
    info = atype.value
    shape = (n,) if info.dimensions == (1,) else (n, *info.dimensions)
    kind = np.dtype(info.dtype).kind
    if kind == "b":
        return rng.random(shape) > 0.5
    if kind in "iu":
        return rng.integers(0, 100, shape).astype(info.dtype)
    return rng.random(shape).astype(info.dtype)


# STRING attributes are read and written one value at a time, so are much slower
NUMERIC_TYPES = [t for t in db.AttributeTypes if t != db.AttributeTypes.STRING]


@pytest.mark.benchmark(group="attribute-read")
@pytest.mark.parametrize("atype", NUMERIC_TYPES, ids=lambda t: t.name)
def test_read_attribute(benchmark, atype):
    obj = db.create_pointcloud_object(POSITIONS)
    db.store_named_attribute(obj, _attribute_values(atype, N), "values", atype=atype)
    benchmark(db.named_attribute, obj, "values")


@pytest.mark.benchmark(group="attribute-write")
@pytest.mark.parametrize("atype", NUMERIC_TYPES, ids=lambda t: t.name)
def test_write_attribute(benchmark, atype):
    obj = db.create_pointcloud_object(POSITIONS)
    values = _attribute_values(atype, N)
    db.store_named_attribute(obj, values, "values", atype=atype)
    benchmark(db.store_named_attribute, obj, values, "values")


@pytest.mark.benchmark(group="attribute-write")
def test_write_attribute_float64(benchmark):
    # float64 data has to be converted to the float32 that Blender stores
    obj = db.create_pointcloud_object(POSITIONS)
    values = POSITIONS.astype(np.float64)
    benchmark(db.store_named_attribute, obj, values, "position")


@pytest.mark.benchmark(group="attribute-array")
def test_attribute_array_read(benchmark):
    bob = db.BlenderObject(db.create_pointcloud_object(POSITIONS))
    benchmark(lambda: bob.position)


@pytest.mark.benchmark(group="attribute-array")
def test_attribute_array_inplace(benchmark):
    position = db.BlenderObject(db.create_pointcloud_object(POSITIONS)).position

    def func():
        position[:, 2] += 1.0

    benchmark(func)


@pytest.mark.benchmark(group="attribute-array")
def test_attribute_array_set_item(benchmark):
    # changing a single value still syncs the whole array
    position = db.BlenderObject(db.create_pointcloud_object(POSITIONS)).position

    def func():
        position[0] = (1.0, 2.0, 3.0)

    benchmark(func)


# small geometry, where the overhead of each call matters more than copying data
SMALL = rng.random((10, 3), dtype=np.float32)


@pytest.mark.benchmark(group="attribute-overhead")
def test_small_read(benchmark):
    obj = db.create_pointcloud_object(SMALL)
    benchmark(db.named_attribute, obj, "position")


@pytest.mark.benchmark(group="attribute-overhead")
def test_small_write(benchmark):
    obj = db.create_pointcloud_object(SMALL)
    benchmark(db.store_named_attribute, obj, SMALL, "position")


@pytest.mark.benchmark(group="attribute-overhead")
def test_small_attribute_array(benchmark):
    bob = db.BlenderObject(db.create_pointcloud_object(SMALL))
    benchmark(lambda: bob.position)
