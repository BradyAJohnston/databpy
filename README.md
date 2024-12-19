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

    array([[0.7498408 , 0.59629339, 0.22656925],
           [0.80878264, 0.00530059, 0.63461214],
           [0.3428221 , 0.63295728, 0.39287162],
           [0.91283602, 0.2825022 , 0.01396279],
           [0.50257456, 0.86614585, 0.94700205],
           [0.38765612, 0.66234422, 0.65887088],
           [0.76694328, 0.28565824, 0.80962974],
           [0.81986648, 0.8590315 , 0.55242574],
           [0.1487771 , 0.69788897, 0.3397437 ],
           [0.74296391, 0.67757684, 0.65559649]])

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

    array([[0.7498408 , 0.59629339, 0.22656925],
           [0.80878264, 0.00530059, 0.63461214],
           [0.3428221 , 0.63295728, 0.39287162],
           [0.91283602, 0.2825022 , 0.01396279],
           [0.50257456, 0.86614585, 0.94700205],
           [0.38765612, 0.66234422, 0.65887088],
           [0.76694328, 0.28565824, 0.80962974],
           [0.81986648, 0.8590315 , 0.55242574],
           [0.1487771 , 0.69788897, 0.3397437 ],
           [0.74296391, 0.67757684, 0.65559649]])

We can clear all of the data from the object and initialise a new mesh
underneath:

``` python
bob.new_from_pydata(np.random.randn(5, 3))
bob.position
```

    array([[ 0.92037618,  1.32638264, -0.57582915],
           [ 0.55520487,  1.12398648, -0.38138115],
           [ 0.38686866,  2.08477449, -0.84588438],
           [-1.26144683, -0.66156071, -0.9639622 ],
           [ 0.12168558, -0.4426263 , -1.3104049 ]])

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
    data = np.array(df[col].to_list(), dtype=np.float32)
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
