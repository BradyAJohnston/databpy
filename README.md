# databpy


[![codecov](https://codecov.io/gh/BradyAJohnston/databpy/graph/badge.svg?token=KFuu67hzAz)](https://codecov.io/gh/BradyAJohnston/databpy)
[![pypi](https://img.shields.io/pypi/v/databpy.png)](https://pypi.org/project/databpy/)
![tests](https://github.com/bradyajohnston/databpy/actions/workflows/tests.yml/badge.svg)
![deployment](https://github.com/bradyajohnston/databpy/actions/workflows/ci-cd.yml/badge.svg)

![](docs/img/notdavid.png)

A set of data-oriented wrappers around the python API of Blender.

This was originally used internally inside of [Molecular
Nodes](https://github.com/BradyAJohnston/MolecularNodes) but was broken
out into a separate python module for re-use in other projects.

## Installation

Available on PyPI, install with pip:

``` bash
pip install databpy
```

> [!CAUTION]
>
> `bpy` (Blender as a python module) is listed as an optional
> dependency, so that if you install `databpy` inside of Blender you
> won’t install a redundant version of `bpy`. If you are using this
> outside of Blender, you will need to specifically request `bpy` with
> either of these methods:
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

Here’s an example on how to store an attribute:

``` python
import numpy as np
import databpy as db

coords = np.array([
    [0, 0, 0],
    [0, 5, 0],
    [5, 0, 0],
    [5, 5, 0]
])

obj = db.create_object(coords, name="Box")
db.store_named_attribute(obj, np.array([10, 20, 31, 42]), "vals")
```

![image](https://github.com/user-attachments/assets/2af6046a-8d73-4881-af63-8ed175fe2136.png)

This module is mainly used to create mesh objects and work with their
attributes. It is built to store and retrieve data using NumPy arrays:

``` python
import numpy as np
import databpy as db
np.random.seed(6)

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

    array([[0.8928602 , 0.3319798 , 0.8212291 ],
           [0.04169663, 0.10765668, 0.59505206],
           [0.52981734, 0.41880742, 0.33540785],
           [0.62251943, 0.43814144, 0.7358821 ],
           [0.5180364 , 0.5788586 , 0.6453551 ],
           [0.99022424, 0.8198582 , 0.41320094],
           [0.8762677 , 0.82375944, 0.05447451],
           [0.7186372 , 0.8021706 , 0.7364066 ],
           [0.7091318 , 0.5409368 , 0.12482417],
           [0.9576473 , 0.4032563 , 0.21695116]], dtype=float32)

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

    AttributeArray(name='position', object='NewObject', mesh='NewObject', domain=POINT, type=FLOAT_VECTOR, shape=(10, 3), dtype=float32)
    array([[0.8928602 , 0.3319798 , 0.8212291 ],
           [0.04169663, 0.10765668, 0.59505206],
           [0.52981734, 0.41880742, 0.33540785],
           [0.62251943, 0.43814144, 0.7358821 ],
           [0.5180364 , 0.5788586 , 0.6453551 ],
           [0.99022424, 0.8198582 , 0.41320094],
           [0.8762677 , 0.82375944, 0.05447451],
           [0.7186372 , 0.8021706 , 0.7364066 ],
           [0.7091318 , 0.5409368 , 0.12482417],
           [0.9576473 , 0.4032563 , 0.21695116]], dtype=float32)

We can clear all of the data from the object and initialise a new mesh
underneath:

``` python
bob.new_from_pydata(np.random.randn(5, 3))
bob.position
```

    AttributeArray(name='position', object='NewObject', mesh='NewObject', domain=POINT, type=FLOAT_VECTOR, shape=(5, 3), dtype=float32)
    array([[ 0.82465386, -1.1764315 ,  1.5644896 ],
           [ 0.7127051 , -0.1810066 ,  0.53419954],
           [-0.58661294, -1.4818532 ,  0.8572476 ],
           [ 0.94309896,  0.11444143, -0.02195668],
           [-2.1271446 , -0.83440745, -0.4655083 ]], dtype=float32)

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

    array([[55.3846, 97.1795,  0.    ],
           [51.5385, 96.0256,  0.    ]], dtype=float32)

``` python
bob.named_attribute("Star")
```

    array([[58.2136, 91.8819,  0.    ],
           [58.1961, 92.215 ,  0.    ]], dtype=float32)
