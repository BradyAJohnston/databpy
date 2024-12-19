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

    array([[0.19533791, 0.8118813 , 0.34549507],
           [0.94876379, 0.53438675, 0.78368348],
           [0.97423679, 0.41086683, 0.48206764],
           [0.27291149, 0.8128683 , 0.54579097],
           [0.93941444, 0.57442093, 0.43480176],
           [0.30820674, 0.23581587, 0.52888143],
           [0.82620269, 0.15830646, 0.21728812],
           [0.19195957, 0.91042393, 0.82571828],
           [0.55324739, 0.07264564, 0.66447401],
           [0.42208153, 0.37834769, 0.92584854]])

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

    array([[0.19533791, 0.8118813 , 0.34549507],
           [0.94876379, 0.53438675, 0.78368348],
           [0.97423679, 0.41086683, 0.48206764],
           [0.27291149, 0.8128683 , 0.54579097],
           [0.93941444, 0.57442093, 0.43480176],
           [0.30820674, 0.23581587, 0.52888143],
           [0.82620269, 0.15830646, 0.21728812],
           [0.19195957, 0.91042393, 0.82571828],
           [0.55324739, 0.07264564, 0.66447401],
           [0.42208153, 0.37834769, 0.92584854]])

We can clear all of the data from the object and initialise a new mesh
underneath:

``` python
bob.new_from_pydata(np.random.randn(5, 3))
bob.position
```

    array([[-0.24637593,  0.48789978, -0.64651048],
           [ 0.01735019,  0.45920223,  0.11351907],
           [ 2.54116821,  0.04286465, -0.87103176],
           [-0.08909958, -0.1191162 , -0.05524581],
           [ 0.75732046, -1.0515815 ,  0.26672497]])
