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

    array([[0.33382925, 0.65230972, 0.40697551],
           [0.15296361, 0.68834376, 0.87484485],
           [0.28670755, 0.69163769, 0.96554619],
           [0.37712002, 0.23925965, 0.11042582],
           [0.18002324, 0.65962017, 0.91494399],
           [0.44024575, 0.27175653, 0.55481952],
           [0.68424481, 0.26874498, 0.20417342],
           [0.17464781, 0.53077883, 0.99934095],
           [0.68674725, 0.33857504, 0.68282163],
           [0.40749231, 0.9381994 , 0.18826957]])

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

    array([[0.33382925, 0.65230972, 0.40697551],
           [0.15296361, 0.68834376, 0.87484485],
           [0.28670755, 0.69163769, 0.96554619],
           [0.37712002, 0.23925965, 0.11042582],
           [0.18002324, 0.65962017, 0.91494399],
           [0.44024575, 0.27175653, 0.55481952],
           [0.68424481, 0.26874498, 0.20417342],
           [0.17464781, 0.53077883, 0.99934095],
           [0.68674725, 0.33857504, 0.68282163],
           [0.40749231, 0.9381994 , 0.18826957]])

We can clear all of the data from the object and initialise a new mesh
underneath:

``` python
bob.new_from_pydata(np.random.randn(5, 3))
bob.position
```

    array([[ 0.83341789,  0.39877525, -1.19136691],
           [ 1.21940732, -2.17261744,  0.5276143 ],
           [ 1.18024218,  2.23327231,  0.94101733],
           [ 0.60895348,  0.01171492, -1.28239524],
           [-0.54698443, -0.6605683 , -1.77002919]])

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
