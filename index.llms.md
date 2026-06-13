# This is databpy!

> **WARNING:**
>
> Active development and refinements are still ongoing. We are not yet past the `1.0` milestone and there may be breaking breaking changes before we get there. `databpy` has matured a lot and the primary interfaces of getting and setting attributes should mostly remain stable.

[![codecov](https://codecov.io/gh/BradyAJohnston/databpy/graph/badge.svg?token=KFuu67hzAz)](https://codecov.io/gh/BradyAJohnston/databpy) [![pypi](https://img.shields.io/pypi/v/databpy.png)](https://pypi.org/project/databpy/) ![tests](https://github.com/bradyajohnston/databpy/actions/workflows/tests.yml/badge.svg) ![deployment](https://github.com/bradyajohnston/databpy/actions/workflows/ci-cd.yml/badge.svg)

![](img/notdavid.png)

This is intended as a cleaner way to work with data and attributes on mesh objects in Blender. The goal is to help make importing and working with tabular datasets from outside of Blender as objects *inside* of blender a whole lot easier.

> **TIP:**
>
> Check out the [**Attributes guid**](attributes.llms.md) for a comprehensive overview of the attribute system, including performance tips, best practices, and examples for all attribute types.

`databpy` originally started as a submodule inside of [Molecular Nodes](https://github.com/BradyAJohnston/MolecularNodes) but has been split off into it’s own package for use by other projects. Some internal code is still quite specific to the use case of Molecular Nodes, but the majority is more general.

## Hello World

The ‘Hello World’ example is storing and retrieving data from a mesh objects inside of Blender.

While the `bpy` API is robust, it is a bit too verbose for what we are after, and there are many particulars that you can’t intuit (you have to store the `value` for floats, `vector` for 2 & 3 component vectors, but `value` for a Quaternion which is a 4-component vector).

See the enums in the API documentation for the different [`AttributeTypes`](api/AttributeTypes.llms.md#databpy.AttributeTypes) and [`AttributeDomains`](api/AttributeDomains.llms.md#databpy.AttributeDomains).

### Regular `bpy` API

``` python
import bpy
import numpy as np

np.random.seed(6)

new_float_values = np.random.randn(8 * 3).reshape(-1, 3)

obj = bpy.data.objects["Cube"]

# create new attribute, then fill with data from a 1D numpy array
att = obj.data.attributes.new("test_float", "FLOAT_VECTOR", "POINT")
att.data.foreach_set("vector", new_float_values.reshape(-1))

# initialise empty array to fill, get data and then reshape to correct dimensions
empty_vector = np.zeros(len(att.data) * 3, dtype=float)
att.data.foreach_get("vector", empty_vector)
empty_vector.reshape((-1, 3))
```

    array([[-0.31178367,  0.72900391,  0.21782079],
           [-0.89909178, -2.48678064,  0.91325152],
           [ 1.12706375, -1.51409328,  1.63929105],
           [-0.42989361,  2.63128066,  0.60182226],
           [-0.33588162,  1.23773789,  0.11112817],
           [ 0.12915125,  0.07612761, -0.15512815],
           [ 0.63422537,  0.810655  ,  0.3548086 ],
           [ 1.81259036, -1.35647583, -0.46363196]])

### `databpy` API

We can get and set values with single function calls. Data types are inferred from the numpy array data types, but can be manually specified. The point domain is the default domain, but domain can also be specified. See the [`AttributeDomains`](api/AttributeDomains.llms.md#databpy.AttributeDomains) for more which domains can be chosen.

``` python
import databpy as db
db.store_named_attribute(obj, new_float_values, "example_values")
db.named_attribute(obj, "example_values")
```

    array([[-0.31178367,  0.7290039 ,  0.2178208 ],
           [-0.8990918 , -2.4867806 ,  0.9132515 ],
           [ 1.1270638 , -1.5140933 ,  1.639291  ],
           [-0.4298936 ,  2.6312807 ,  0.60182226],
           [-0.33588162,  1.2377379 ,  0.11112817],
           [ 0.12915125,  0.07612761, -0.15512815],
           [ 0.63422537,  0.810655  ,  0.3548086 ],
           [ 1.8125904 , -1.3564758 , -0.46363196]], dtype=float32)

## A more friendly Blender Object (bob)

Doing some common data-oriented operations on objects in Blender can be a bit of a pain, so `databpy` provides a [`BlenderObject`](api/BlenderObject.llms.md#databpy.BlenderObject) class that wraps mesh objects and provides some convenience functions.

The most useful are the [`store_named_attribute()`](api/BlenderObject.llms.md#databpy.BlenderObject.store_named_attribute) and [`named_attribute()`](api/BlenderObject.llms.md#databpy.BlenderObject.named_attribute) methods that just work on the mesh object, so you can quickly get and set attributes with bob.

``` python
bob = db.BlenderObject(bpy.data.objects["Cube"])

bob.store_named_attribute(new_float_values, "example_values")
bob.named_attribute("example_values")
```

    array([[-0.31178367,  0.7290039 ,  0.2178208 ],
           [-0.8990918 , -2.4867806 ,  0.9132515 ],
           [ 1.1270638 , -1.5140933 ,  1.639291  ],
           [-0.4298936 ,  2.6312807 ,  0.60182226],
           [-0.33588162,  1.2377379 ,  0.11112817],
           [ 0.12915125,  0.07612761, -0.15512815],
           [ 0.63422537,  0.810655  ,  0.3548086 ],
           [ 1.8125904 , -1.3564758 , -0.46363196]], dtype=float32)
