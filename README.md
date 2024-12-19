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

    {'FINISHED'}

``` python
import numpy as np
import databpy as db

# Create a mesh object

random_verts = np.random.rand(10, 3)

obj = db.create_object(random_verts, name="RandomMesh")

obj.name
```

    'RandomMesh'

``` python
db.named_attribute(obj, 'position')
```

    array([[0.74675053, 0.99931186, 0.48985159],
           [0.34094697, 0.31241801, 0.30594653],
           [0.31175202, 0.65143555, 0.63226628],
           [0.85441101, 0.74514931, 0.58964694],
           [0.4720692 , 0.2637527 , 0.14295585],
           [0.14470775, 0.16943374, 0.1675023 ],
           [0.25198391, 0.47381482, 0.82664227],
           [0.18684188, 0.373088  , 0.43143356],
           [0.63306928, 0.86285251, 0.725779  ],
           [0.89526188, 0.37104774, 0.90417325]])

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

    array([[0.74675053, 0.99931186, 0.48985159],
           [0.34094697, 0.31241801, 0.30594653],
           [0.31175202, 0.65143555, 0.63226628],
           [0.85441101, 0.74514931, 0.58964694],
           [0.4720692 , 0.2637527 , 0.14295585],
           [0.14470775, 0.16943374, 0.1675023 ],
           [0.25198391, 0.47381482, 0.82664227],
           [0.18684188, 0.373088  , 0.43143356],
           [0.63306928, 0.86285251, 0.725779  ],
           [0.89526188, 0.37104774, 0.90417325]])

We can clear all of the data from the object and initialise a new mesh
underneath:

``` python
bob.new_from_pydata(np.random.randn(5, 3))
bob.position
```

    array([[ 0.56661713,  0.63418388,  0.6149258 ],
           [-0.7188437 ,  1.23112321, -0.10584434],
           [ 2.00507832,  1.11055791,  1.74327374],
           [ 1.48533213,  0.21335189,  0.66159528],
           [-0.51439518,  0.26141584,  0.21525437]])
