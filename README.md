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

    array([[0.53582048, 0.01025325, 0.671498  ],
           [0.52546251, 0.33915451, 0.63990462],
           [0.25647345, 0.47855887, 0.7207343 ],
           [0.46506837, 0.44545677, 0.05130248],
           [0.41610014, 0.57358569, 0.08732817],
           [0.54886872, 0.54106748, 0.00630351],
           [0.27543187, 0.19321527, 0.65988147],
           [0.568762  , 0.04052029, 0.94017988],
           [0.50326049, 0.01813961, 0.27365947],
           [0.32320163, 0.71272546, 0.71071666]])

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

    array([[0.53582048, 0.01025325, 0.671498  ],
           [0.52546251, 0.33915451, 0.63990462],
           [0.25647345, 0.47855887, 0.7207343 ],
           [0.46506837, 0.44545677, 0.05130248],
           [0.41610014, 0.57358569, 0.08732817],
           [0.54886872, 0.54106748, 0.00630351],
           [0.27543187, 0.19321527, 0.65988147],
           [0.568762  , 0.04052029, 0.94017988],
           [0.50326049, 0.01813961, 0.27365947],
           [0.32320163, 0.71272546, 0.71071666]])

We can clear all of the data from the object and initialise a new mesh
underneath:

``` python
bob.new_from_pydata(np.random.randn(5, 3))
bob.position
```

    array([[-0.3981916 ,  0.76089966,  0.87074465],
           [ 0.00484101,  1.1918782 , -0.60438061],
           [ 0.01859177, -0.54387122,  1.42838871],
           [ 1.17083395, -0.07674965, -0.95345807],
           [-2.01008439,  0.48055843, -1.04187691]])

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
