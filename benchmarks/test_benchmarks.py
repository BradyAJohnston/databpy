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
