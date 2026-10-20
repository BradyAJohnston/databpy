# This is databpy!

> **WARNING:**
>
> databpy is still before its `1.0` release, so there may be breaking changes before then. The main interfaces for getting and setting attributes are expected to stay stable.

[![codecov](https://codecov.io/gh/BradyAJohnston/databpy/graph/badge.svg?token=KFuu67hzAz)](https://codecov.io/gh/BradyAJohnston/databpy) [![pypi](https://img.shields.io/pypi/v/databpy.png)](https://pypi.org/project/databpy/) ![deployment](https://github.com/bradyajohnston/databpy/actions/workflows/ci-cd.yml/badge.svg)

![](img/notdavid.png)

databpy reads and writes the attributes of mesh, curves and point cloud objects in Blender as NumPy arrays. It is built for importing tabular data from outside Blender as objects *inside* Blender, and working with it there. It supports Blender 5.1 and later.

> **TIP:**
>
> The [**attributes guide**](attributes.llms.md) covers the attribute system: the attribute types and domains, reading and writing attributes, performance, and errors.

`databpy` started as a submodule of [Molecular Nodes](https://github.com/BradyAJohnston/MolecularNodes) and was split off into its own package for use by other projects. Some internal code is still specific to Molecular Nodes, but most of it is general.

## Hello world

The ‘Hello world’ example stores data on a mesh object in Blender and reads it back.

The `bpy` API needs several calls for this, and the property that holds the values depends on the type: `value` for floats, `vector` for 2 and 3 component vectors, but `value` for a quaternion, which also has 4 components.

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

Getting and setting values takes one function call each. The attribute type is inferred from the array’s dtype and shape, or can be given explicitly. Attributes are stored on the point domain unless another domain is given; see [`AttributeDomains`](api/AttributeDomains.llms.md#databpy.AttributeDomains) for the domains available.

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

## A friendlier Blender object (bob)

The [`BlenderObject`](api/BlenderObject.llms.md#databpy.BlenderObject) class wraps a mesh, curves or point cloud object and adds methods for data-oriented work on it.

Its [`store_named_attribute()`](api/BlenderObject.llms.md#databpy.BlenderObject.store_named_attribute) and [`named_attribute()`](api/BlenderObject.llms.md#databpy.BlenderObject.named_attribute) methods get and set attributes on the wrapped object.

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

[`create_bob()`](api/create_bob.llms.md#databpy.create_bob) creates a mesh object from an array of vertex positions and wraps it. Attributes can also be read as properties and items, such as `bob.position` and `bob["position"]`, which return an [`AttributeArray`](api/AttributeArray.llms.md#databpy.AttributeArray) that writes changes back to Blender:

``` python
np.random.seed(6)
bob = db.create_bob(np.random.rand(10, 3), name="RandomMesh")

bob.position[:, 2] += 1.0
bob["position"]
```

    AttributeArray(name='position', object='RandomMesh', mesh='RandomMesh', domain=POINT, type=FLOAT_VECTOR, shape=(10, 3), dtype=float32)
    array([[0.8928602 , 0.3319798 , 1.8212291 ],
           [0.04169663, 0.10765668, 1.595052  ],
           [0.52981734, 0.41880742, 1.3354079 ],
           [0.62251943, 0.43814144, 1.735882  ],
           [0.5180364 , 0.5788586 , 1.6453551 ],
           [0.99022424, 0.8198582 , 1.413201  ],
           [0.8762677 , 0.82375944, 1.0544745 ],
           [0.7186372 , 0.8021706 , 1.7364066 ],
           [0.7091318 , 0.5409368 , 1.1248242 ],
           [0.9576473 , 0.4032563 , 1.2169511 ]], dtype=float32)

[`new_from_pydata()`](api/BlenderObject.llms.md#databpy.BlenderObject.new_from_pydata) clears the geometry of the object’s mesh and fills it with new vertices, edges and faces:

``` python
bob.new_from_pydata(np.random.randn(5, 3))
bob.position
```

    AttributeArray(name='position', object='RandomMesh', mesh='RandomMesh', domain=POINT, type=FLOAT_VECTOR, shape=(5, 3), dtype=float32)
    array([[ 0.82465386, -1.1764315 ,  1.5644896 ],
           [ 0.7127051 , -0.1810066 ,  0.53419954],
           [-0.58661294, -1.4818532 ,  0.8572476 ],
           [ 0.94309896,  0.11444143, -0.02195668],
           [-2.1271446 , -0.83440745, -0.4655083 ]], dtype=float32)

## Importing a table with Polars

Columns of a data frame can be stored as attributes. Here each column of a JSON table holds a list of 3D points, which are stored as `FLOAT_VECTOR` attributes on a new object with one vertex per row:

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
df = df.explode(columns_to_explode, empty_as_null=True)

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
