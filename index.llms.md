# This is databpy!

> **WARNING:**
>
> databpy is still before its `1.0` release, so there may be breaking changes before then. The main interfaces for getting and setting attributes are expected to stay stable.

[![codecov](https://codecov.io/gh/BradyAJohnston/databpy/graph/badge.svg?token=KFuu67hzAz)](https://codecov.io/gh/BradyAJohnston/databpy) [![pypi](https://img.shields.io/pypi/v/databpy.png)](https://pypi.org/project/databpy/) ![deployment](https://github.com/bradyajohnston/databpy/actions/workflows/ci-cd.yml/badge.svg)

![](img/notdavid.png)

databpy reads and writes the attributes of mesh, curves and point cloud objects in Blender as NumPy arrays. It is built for importing tabular data from outside Blender as objects *inside* Blender, and working with it there. It supports Blender 5.1 and later.

> **TIP:**
>
> Three guides cover the attribute system: [Attributes](attributes.llms.md) for domains, typed arrays and errors, [Syncing with Blender](syncing.llms.md) for how arrays write changes back and when to use copies, and [Grease pencil and evaluated geometry](geometry.llms.md) for drawings and the output of Geometry Nodes.

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

Each domain of the object has a dictionary-style view, such as `bob.point` and `bob.face`, and typed arrays such as [`db.vec3`](api/vec3.llms.md#databpy.vec3) and [`db.color`](api/color.llms.md#databpy.color) state the type an attribute is stored as. Together they say where an attribute lives and what it holds:

``` python
cube = db.BlenderObject(bpy.data.objects["Cube"])

cube.face["tint"] = db.color(np.random.rand(len(cube.face), 4))
cube.face["tint", db.color]  # checks the type, which type checkers also see
```

    AttributeArray(name='tint', object='Cube', mesh='Cube', domain=FACE, type=FLOAT_COLOR, shape=(6, 4), dtype=float32)
    array([[0.71727586, 0.99420744, 0.25561404, 0.6713094 ],
           [0.59900594, 0.7173321 , 0.93734956, 0.35180977],
           [0.2536341 , 0.4024725 , 0.74651074, 0.72407055],
           [0.40610778, 0.9893798 , 0.45049927, 0.37380844],
           [0.7096286 , 0.08245856, 0.39837292, 0.77088094],
           [0.76475096, 0.28385937, 0.18954219, 0.47125095]], dtype=float32)

[`new_from_pydata()`](api/BlenderObject.llms.md#databpy.BlenderObject.new_from_pydata) clears the geometry of the object’s mesh and fills it with new vertices, edges and faces:

``` python
bob.new_from_pydata(np.random.randn(5, 3))
bob.position
```

    AttributeArray(name='position', object='RandomMesh', mesh='RandomMesh', domain=POINT, type=FLOAT_VECTOR, shape=(5, 3), dtype=float32)
    array([[ 1.2184806 , -0.85750145, -0.56147087],
           [-1.0335199 ,  0.35877097,  1.0736814 ],
           [-0.37550473,  0.39636758, -0.47144628],
           [ 2.3366077 ,  1.5027856 , -0.5954597 ],
           [ 0.52834105,  0.9398248 ,  0.4262854 ]], dtype=float32)

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
