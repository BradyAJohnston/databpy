# `BlenderObject` class (bob)


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

    'RandomMesh.001'

``` python
db.named_attribute(obj, 'position')
```

    array([[0.17452642, 0.45645952, 0.19546226],
           [0.81541622, 0.39680132, 0.87869591],
           [0.92496204, 0.16035524, 0.97199863],
           [0.34075448, 0.5464862 , 0.02298789],
           [0.0192579 , 0.35214618, 0.56019056],
           [0.49805972, 0.46989357, 0.15057611],
           [0.98557359, 0.7825923 , 0.40234712],
           [0.1231764 , 0.33543932, 0.66668808],
           [0.85444725, 0.76267177, 0.93717819],
           [0.37655553, 0.65764296, 0.72231734]])

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

    array([[0.17452642, 0.45645952, 0.19546226],
           [0.81541622, 0.39680132, 0.87869591],
           [0.92496204, 0.16035524, 0.97199863],
           [0.34075448, 0.5464862 , 0.02298789],
           [0.0192579 , 0.35214618, 0.56019056],
           [0.49805972, 0.46989357, 0.15057611],
           [0.98557359, 0.7825923 , 0.40234712],
           [0.1231764 , 0.33543932, 0.66668808],
           [0.85444725, 0.76267177, 0.93717819],
           [0.37655553, 0.65764296, 0.72231734]])

We can clear all of the data from the object and initialise a new mesh
underneath:

``` python
bob.new_from_pydata(np.random.randn(5, 3))
bob.position
```

    array([[ 1.30187321, -0.8981759 , -0.24894828],
           [ 0.0452443 ,  0.66260809,  0.02360807],
           [-0.04097848, -0.16771786,  3.13003659],
           [-0.85789645, -0.51301759,  0.31468081],
           [ 0.86041909, -0.50534254,  0.36779848]])
