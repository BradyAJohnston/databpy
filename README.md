# databpy

[![pypi](https://img.shields.io/pypi/v/databpy)](https://pypi.org/project/databpy/)
[![codecov](https://codecov.io/gh/BradyAJohnston/databpy/graph/badge.svg?token=KFuu67hzAz)](https://codecov.io/gh/BradyAJohnston/databpy)
[![CodSpeed](https://img.shields.io/endpoint?url=https://codspeed.io/badge.json)](https://app.codspeed.io/BradyAJohnston/databpy?utm_source=badge)
![deployment](https://github.com/bradyajohnston/databpy/actions/workflows/ci-cd.yml/badge.svg)

![](https://raw.githubusercontent.com/BradyAJohnston/databpy/main/docs/img/notdavid.png)

databpy reads and writes the attributes of mesh, curves and point cloud objects in Blender as NumPy arrays, and creates those objects from arrays. It supports Blender 5.1 and later.

```python
import numpy as np
import databpy as db

# create a mesh object from an (n, 3) array of vertex positions
bob = db.create_bob(np.random.rand(100, 3), name="Points")

# store and read attributes as NumPy arrays; the type is inferred from the dtype
bob.store_named_attribute(np.arange(100), "id")
ids = bob.named_attribute("id")

# attributes as arrays that write changes back to Blender
bob.position[:, 2] += 1.0
bob["id"][:10] = -1
```

`store_named_attribute()` and `named_attribute()` are named after the Store Named Attribute and Named Attribute nodes in Geometry Nodes.

## Performance

databpy builds meshes by writing arrays straight to their attributes, rather than through `Mesh.from_pydata()`, and an attribute array writes back only the values that change:

| Operation                                      | `bpy`   | databpy  | Speedup |
| ---------------------------------------------- | ------- | -------- | ------- |
| Mesh from 100,000 vertices                     | 37 ms   | 0.14 ms  | ~260x   |
| Mesh from 100,000 vertices and 99,999 edges    | 62 ms   | 0.24 ms  | ~260x   |
| Mesh from 90,000 vertices and 89,401 quads     | 101 ms  | 5.0 ms   | ~20x    |
| Write 10 values of a 1,000,000 point attribute | 0.28 ms | 0.006 ms | ~45x    |

The `bpy` column uses `Mesh.from_pydata()` for meshes, and for the attribute write a `foreach_get` and `foreach_set` round trip of the whole attribute. Times are medians of the workloads in [`benchmarks/test_benchmarks.py`](https://github.com/BradyAJohnston/databpy/blob/main/benchmarks/test_benchmarks.py), measured with bpy 5.2.1 and Python 3.13 on an AMD Ryzen 9 9950X (Linux), and vary by machine. [CodSpeed](https://app.codspeed.io/BradyAJohnston/databpy) tracks the benchmarks on every pull request.

## Installation

```bash
pip install databpy
```

`bpy` (Blender as a Python module) is an optional dependency, so installing databpy inside Blender doesn't install a second copy of `bpy`. To use databpy outside Blender, install `bpy` with it:

```bash
pip install "databpy[bpy]"
```

## Supported Blender versions

| Blender     | Tests                                                                                                                                                                            |
| ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 5.1         | [![Blender 5.1](https://github.com/BradyAJohnston/databpy/actions/workflows/tests-5.1.yml/badge.svg)](https://github.com/BradyAJohnston/databpy/actions/workflows/tests-5.1.yml) |
| 5.2         | [![Blender 5.2](https://github.com/BradyAJohnston/databpy/actions/workflows/tests-5.2.yml/badge.svg)](https://github.com/BradyAJohnston/databpy/actions/workflows/tests-5.2.yml) |
| 5.3 (beta)  | [![Blender 5.3](https://github.com/BradyAJohnston/databpy/actions/workflows/tests-5.3.yml/badge.svg)](https://github.com/BradyAJohnston/databpy/actions/workflows/tests-5.3.yml) |
| 5.4 (alpha) | [![Blender 5.4](https://github.com/BradyAJohnston/databpy/actions/workflows/tests-5.4.yml/badge.svg)](https://github.com/BradyAJohnston/databpy/actions/workflows/tests-5.4.yml) |

databpy requires Python 3.13, the version Blender 5.1 and 5.2 use.

## Documentation

- [Getting started](https://bradyajohnston.github.io/databpy/): storing and reading attributes, `BlenderObject`, and importing a table with Polars
- [Attributes guide](https://bradyajohnston.github.io/databpy/attributes.html): attribute types and domains, syncing, performance and errors
- [API reference](https://bradyajohnston.github.io/databpy/api/)
- [Changelog](https://bradyajohnston.github.io/databpy/changelog.html)

`databpy` started inside [Molecular Nodes](https://github.com/BradyAJohnston/MolecularNodes) and was split into a separate package for use in other projects, similarly to [`nodebpy`](https://github.com/BradyAJohnston/nodebpy).
