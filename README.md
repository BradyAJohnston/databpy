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

    'RandomMesh.005'

``` python
db.named_attribute(obj, 'position')
```

    array([[0.31141922, 0.95264083, 0.5174194 ],
           [0.07187664, 0.08571111, 0.86926758],
           [0.52204382, 0.81694955, 0.59866261],
           [0.97583383, 0.78864473, 0.86882359],
           [0.94398558, 0.97538602, 0.25609457],
           [0.53115636, 0.00953662, 0.2476171 ],
           [0.36509034, 0.44710255, 0.05920378],
           [0.20393749, 0.57369787, 0.92388427],
           [0.39632952, 0.53060335, 0.90295321],
           [0.85831082, 0.25212002, 0.44943741]])

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

    array([[0.31141922, 0.95264083, 0.5174194 ],
           [0.07187664, 0.08571111, 0.86926758],
           [0.52204382, 0.81694955, 0.59866261],
           [0.97583383, 0.78864473, 0.86882359],
           [0.94398558, 0.97538602, 0.25609457],
           [0.53115636, 0.00953662, 0.2476171 ],
           [0.36509034, 0.44710255, 0.05920378],
           [0.20393749, 0.57369787, 0.92388427],
           [0.39632952, 0.53060335, 0.90295321],
           [0.85831082, 0.25212002, 0.44943741]])

We can clear all of the data from the object and initialise a new mesh
underneath:

``` python
bob.new_from_pydata(np.random.randn(5, 3))
bob.position
```

    array([[ 2.13592982, -0.83191729, -0.88964295],
           [-0.52801269,  0.64697677,  0.38492382],
           [ 1.93874156, -1.91766572, -0.98241842],
           [ 0.80909991, -1.18728089, -0.33013529],
           [-0.44700807,  0.22891042,  1.05114532]])
