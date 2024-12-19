# databpy


[![codecov](https://codecov.io/gh/BradyAJohnston/databpy/graph/badge.svg?token=KFuu67hzAz)](https://codecov.io/gh/BradyAJohnston/databpy)
![PyPI - Version](https://img.shields.io/pypi/v/databpy.png) ![example
workflow](https://github.com/bradyajohnston/databpy/actions/workflows/tests.yml/badge.svg)
![example
workflow](https://github.com/bradyajohnston/databpy/actions/workflows/ci-cd.yml/badge.svg)

A set of data-oriented wrappers around the python API of Blender.

## Installation

Available on PyPI, install with pip:

``` bash
pip install databpy
```

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

    array([[0.25153503, 0.44389936, 0.82651126],
           [0.90864307, 0.87539542, 0.83167022],
           [0.52049249, 0.35679546, 0.77222192],
           [0.61770487, 0.32215825, 0.1973864 ],
           [0.27137873, 0.34053022, 0.11584114],
           [0.94821477, 0.25533059, 0.26194656],
           [0.02210427, 0.97262025, 0.40936294],
           [0.83268362, 0.12833712, 0.14741039],
           [0.84197783, 0.73525953, 0.16990589],
           [0.41872299, 0.04931316, 0.89335144]])

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

    array([[0.25153503, 0.44389936, 0.82651126],
           [0.90864307, 0.87539542, 0.83167022],
           [0.52049249, 0.35679546, 0.77222192],
           [0.61770487, 0.32215825, 0.1973864 ],
           [0.27137873, 0.34053022, 0.11584114],
           [0.94821477, 0.25533059, 0.26194656],
           [0.02210427, 0.97262025, 0.40936294],
           [0.83268362, 0.12833712, 0.14741039],
           [0.84197783, 0.73525953, 0.16990589],
           [0.41872299, 0.04931316, 0.89335144]])

We can clear all of the data from the object and initialise a new mesh
underneath:

``` python
bob.new_from_pydata(np.random.randn(5, 3))
bob.position
```

    array([[ 0.08886742,  2.16487241, -0.93285018],
           [ 0.19166082, -0.76304299, -0.29899105],
           [ 0.29144779, -1.15066338, -0.37192449],
           [-0.70251977,  0.69413024,  0.78812218],
           [-0.59531879,  1.05508363, -0.71289873]])

## Example with Polars data

``` python
import polars as pl
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
    data = np.array(df[col].to_list(), dtype=np.float32)
    bob.store_named_attribute(np.array(data.tolist()), col)

bob.named_attribute("Dino")
```

    array([[55.38460159, 97.17949677,  0.        ],
           [51.53850174, 96.02559662,  0.        ]])

``` python
bob.named_attribute("Star")
```

    array([[58.21360016, 91.88189697,  0.        ],
           [58.19609833, 92.21499634,  0.        ]])
