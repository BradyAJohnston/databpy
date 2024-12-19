# databpy


[![codecov](https://codecov.io/gh/BradyAJohnston/databpy/graph/badge.svg?token=KFuu67hzAz)](https://codecov.io/gh/BradyAJohnston/databpy)
[![PyPI version](https://img.shields.io/pypi/v/databpy)](https://pypi.org/project/databpy/) ![example
workflow](https://github.com/bradyajohnston/databpy/actions/workflows/tests.yml/badge.svg)
![example
workflow](https://github.com/bradyajohnston/databpy/actions/workflows/ci-cd.yml/badge.svg)

A set of data-oriented wrappers around the python API of Blender.

## Installation

Available on PyPI, install with pip:

``` bash
pip install databpy
```

> [!CAUTION]
>
> `bpy` (Blener as a python module) is listed as an optional dependency,
> so that if you install `databpy` inside of Blender you won’t install a
> redundant version of `bpy`. If you are using this outside of Blender,
> you will need to specifically request `bpy` with either of these
> methods:
>
> ``` bash
> # install wtih bpy dependency
> pip install 'databpy[bpy]'
>
> # install both packages
> pip install databpy bpy
>
> # install with all optional dependencies
> pip install 'databpy[all]'
> ```

## Usage

The main use cases are to create objects, store and retrieve attributes
from them. The functions are named around nodes in Geometry Nodes
`Store Named Attribute` and `Named Attribute`

``` python
import databpy as db

db.store_named_attribute() # store a named attribute on a mesh object
db.named_attribute()       # retrieve a named attribute from a mesh object
```

Mostly oriented around creating mesh objects, assigning and getting back
attributes from them. Currently designed around storing and retrieving
`numpy` data types:

``` python
import numpy as np
import databpy as db

# Create a mesh object

random_verts = np.random.rand(10, 3)

obj = db.create_object(random_verts, name="RandomMesh")

obj.name
```

    'RandomMesh'

Access attributes from the object’s mesh.

``` python
db.named_attribute(obj, 'position')
```

    array([[0.73641926, 0.48488575, 0.72500235],
           [0.93242395, 0.23630837, 0.10771675],
           [0.61948055, 0.00335572, 0.08878344],
           [0.71459097, 0.13228028, 0.26439887],
           [0.06164043, 0.32223272, 0.03915258],
           [0.26988253, 0.96634519, 0.9258244 ],
           [0.46986273, 0.04557773, 0.40641493],
           [0.86258143, 0.20877074, 0.58634591],
           [0.45481128, 0.26667479, 0.37325892],
           [0.98243082, 0.89934868, 0.30204201]])

### `BlenderObject` class (bob)

This is a convenience class that wraps around the `bpy.types.Object`,
and provides access to all of the useful functions. We can wrap an
existing Object or return one when creating a new object.

This just gives us access to the `named_attribute()` and
`store_named_attribute()` functions on the object class, but also
provides a more intuitive way to access the object’s attributes.

``` python
bob = db.BlenderObject(obj)       # wraps the existing object 
bob = db.create_bob(random_verts) # creates a new object and returns it already wrapped

# these two are identical
bob.named_attribute('position')
bob.position
```

    array([[0.73641926, 0.48488575, 0.72500235],
           [0.93242395, 0.23630837, 0.10771675],
           [0.61948055, 0.00335572, 0.08878344],
           [0.71459097, 0.13228028, 0.26439887],
           [0.06164043, 0.32223272, 0.03915258],
           [0.26988253, 0.96634519, 0.9258244 ],
           [0.46986273, 0.04557773, 0.40641493],
           [0.86258143, 0.20877074, 0.58634591],
           [0.45481128, 0.26667479, 0.37325892],
           [0.98243082, 0.89934868, 0.30204201]])

We can clear all of the data from the object and initialise a new mesh
underneath:

``` python
bob.new_from_pydata(np.random.randn(5, 3))
bob.position
```

    array([[-0.71264023,  0.32978976, -0.63028884],
           [-0.92074728,  0.11562137, -0.18979079],
           [-0.66534227,  0.53521448,  0.65792871],
           [ 0.61330676,  1.39815307,  0.59663987],
           [ 1.02735949,  0.57145709, -0.6408332 ]])

## Example with Polars data

``` python
import polars as pl
import databpy as db
from io import StringIO

json_file = StringIO("""
{
  "Dino": [
    [55.3846, 97.1795, 0.0],
    [51.5385, 96.0256, 0.0]
  ],
  "Star": [
    [58.2136, 91.8819, 0.0],
    [58.1961, 92.215, 0.0]
  ]
}
""")

df = pl.read_json(json_file)
columns_to_explode = [col for col in df.columns if df[col].dtype == pl.List(pl.List)]
df = df.explode(columns_to_explode)

vertices = np.zeros((len(df), 3), dtype=np.float32)
bob = db.create_bob(vertices, name="DinoStar")

for col in df.columns:
    data = np.vstack(df.get_column(col).to_numpy())
    bob.store_named_attribute(data, col)

bob.named_attribute("Dino")
```

    array([[55.38460159, 97.17949677,  0.        ],
           [51.53850174, 96.02559662,  0.        ]])

``` python
bob.named_attribute("Star")
```

    array([[58.21360016, 91.88189697,  0.        ],
           [58.19609833, 92.21499634,  0.        ]])
