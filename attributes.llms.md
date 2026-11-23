# Attributes

This guide explains how to read and write the attributes of an object with databpy: choosing the domain an attribute is stored on, and stating the type of its values. It assumes you know NumPy arrays and have used Blender. Two more guides follow on from this one:

- [Syncing with Blender](syncing.llms.md) explains how the arrays you read write changes back to Blender, and when to work with copies.
- [Grease pencil and evaluated geometry](geometry.llms.md) covers attributes that aren’t stored on the object itself: the drawings of a grease pencil object, and the output of Geometry Nodes.

## Attributes, domains and types

Blender stores the data of a geometry as attributes. An attribute is a named array with one value for each element of a domain, such as the vertices or faces of a mesh. Vertex positions, UV coordinates and vertex colors are all attributes. For example:

- Vertex positions are a `FLOAT_VECTOR` attribute named `"position"` on the `POINT` domain.
- Face materials are an `INT` attribute on the `FACE` domain.
- UV maps are `FLOAT2` attributes on the `CORNER` domain.

Every attribute has a domain, which is the kind of element it has a value for, and a type, which is what each value is. databpy reads and writes attributes as NumPy arrays, and you can state both the domain and the type in code:

``` python
import databpy as db
import numpy as np
import bpy

bob = db.BlenderObject(bpy.data.objects["Cube"])

# the domain comes from `bob.face`, and the type from `db.vec3`
bob.face["normal_offset"] = db.vec3(np.zeros((len(bob.face), 3)))
bob["normal_offset"]
```

    AttributeArray(name='normal_offset', object='Cube', mesh='Cube', domain=FACE, type=FLOAT_VECTOR, shape=(6, 3), dtype=float32)
    array([[0., 0., 0.],
           [0., 0., 0.],
           [0., 0., 0.],
           [0., 0., 0.],
           [0., 0., 0.],
           [0., 0., 0.]], dtype=float32)

Attribute names are unique within a geometry, so `bob.face["normal_offset"]` and `bob["normal_offset"]` read the same attribute. You only need to give the domain when you create an attribute.

## Choose a domain

A [`BlenderObject`](api/BlenderObject.llms.md#databpy.BlenderObject) has a domain view, [`AttributeDomainView`](api/AttributeDomainView.llms.md#databpy.AttributeDomainView), for each domain. A domain view works like a dictionary of the attributes on its domain. The following table lists the domain views:

| Domain view | Domain | Elements | Example uses |
|----|----|----|----|
| `bob.point` | `POINT` | Vertices, curve control points, point cloud points | Positions, vertex colors, velocities |
| `bob.edge` | `EDGE` | Mesh edges | Edge weights, crease values |
| `bob.face` | `FACE` | Mesh faces | Material indices, face areas |
| `bob.corner` | `CORNER` | Face corners, one for each vertex of each face | UV coordinates, split normals |
| `bob.curve` | `CURVE` | Curve splines | Per-spline properties |
| `bob.layer` | `LAYER` | Grease pencil layers | Per-layer properties |

The length of a domain view is the number of elements in its domain:

``` python
print(len(bob.point), len(bob.edge), len(bob.face), len(bob.corner))
```

    8 12 6 24

Storing on a domain view creates the attribute on that domain, or writes to the existing attribute:

``` python
bob.face["area"] = np.linspace(0, 1, len(bob.face))
bob.edge["crease_weight"] = np.ones(len(bob.edge))

print(bob.face.list_attributes())
"area" in bob.face, "area" in bob.point
```

    ['.select_poly', 'sharp_face', '.uv_select_face', 'normal_offset', 'area']

    (True, False)

A domain view only reads and writes attributes on its own domain. Using an attribute that exists on another domain raises a [`NamedAttributeError`](api/NamedAttributeError.llms.md#databpy.NamedAttributeError):

``` python
try:
    bob.point["area"]
except db.NamedAttributeError as e:
    print(e)
```

    Attribute `area` is on the `FACE` domain, not `POINT`.

`bob["name"]` reads an attribute on any domain. When `bob["name"] = values` creates an attribute, it stores it on the `POINT` domain.

> **IMPORTANT:**
>
> An array you store needs one value for each element of the domain. A cube has 8 vertices, 12 edges, 6 faces and 24 corners, so arrays stored on it need those lengths. A domain that the geometry doesn’t have, such as `bob.face` on a point cloud, has a length of 0 and can’t store attributes.

## State the type

Blender names each attribute type with a string, such as `FLOAT_VECTOR` for 3D vectors. The [`AttributeTypes`](api/AttributeTypes.llms.md#databpy.AttributeTypes) enum lists these names. For each type, databpy has a typed array: a NumPy array that states the attribute type it is stored as. Blender stores values as 32-bit numbers or smaller, so every typed array has one of the dtypes `float32`, `int32`, `int16`, `int8`, `uint8` or `bool`, or `str` for text. The following table lists the typed arrays:

| Typed array | Blender type | Value | dtype | Array shape |
|----|----|----|----|----|
| [`db.float32`](api/float32.llms.md#databpy.float32) | `FLOAT` | float | `float32` | `(n,)` |
| [`db.vec2`](api/vec2.llms.md#databpy.vec2) | `FLOAT2` | 2D vector | `float32` | `(n, 2)` |
| [`db.vec3`](api/vec3.llms.md#databpy.vec3) | `FLOAT_VECTOR` | 3D vector | `float32` | `(n, 3)` |
| [`db.vec4`](api/vec4.llms.md#databpy.vec4) | `FLOAT4` | 4D vector (Blender 5.2+) | `float32` | `(n, 4)` |
| [`db.color`](api/color.llms.md#databpy.color) | `FLOAT_COLOR` | linear RGBA color | `float32` | `(n, 4)` |
| [`db.srgb`](api/srgb.llms.md#databpy.srgb) | `FLOAT_COLOR` | sRGB RGBA color, stored as linear | `float32` | `(n, 4)` |
| [`db.color8`](api/color8.llms.md#databpy.color8) | `BYTE_COLOR` | sRGB RGBA color | `uint8` | `(n, 4)` |
| [`db.quat`](api/quat.llms.md#databpy.quat) | `QUATERNION` | (w, x, y, z) rotation | `float32` | `(n, 4)` |
| [`db.mat4`](api/mat4.llms.md#databpy.mat4) | `FLOAT4X4` | 4x4 matrix, row-major | `float32` | `(n, 4, 4)` |
| [`db.int32`](api/int32.llms.md#databpy.int32) | `INT` | integer | `int32` | `(n,)` |
| [`db.int8`](api/int8.llms.md#databpy.int8) | `INT8` | small integer | `int8` | `(n,)` |
| [`db.ivec2`](api/ivec2.llms.md#databpy.ivec2) | `INT32_2D` | 2D integer vector | `int32` | `(n, 2)` |
| [`db.sivec2`](api/sivec2.llms.md#databpy.sivec2) | `INT16_2D` | 2D small integer vector | `int16` | `(n, 2)` |
| [`db.boolean`](api/boolean.llms.md#databpy.boolean) | `BOOLEAN` | true or false | `bool` | `(n,)` |
| [`db.string`](api/string.llms.md#databpy.string) | `STRING` | text | `str` | `(n,)` |

### Write typed data

Wrap data in a typed array, such as `db.vec3(data)`, to state the type it is stored as. The typed array checks that the data has the right shape and casts it to the type’s dtype, so it is ready to store. A wrapped array isn’t linked to any attribute until you store it:

``` python
offsets = db.vec3(np.random.rand(8, 3))  # float64 is cast to float32
print(type(offsets).__name__, offsets.dtype, offsets.shape)

bob.point["offset"] = offsets
```

    vec3 float32 (8, 3)

Wrapping data that already has the right dtype doesn’t copy it.

Several types share a shape. A `(n, 4)` float array could be a 4D vector, a color or a quaternion, so the typed array decides which one is stored:

``` python
rgba = np.random.rand(8, 4)

bob.point["tint"] = db.color(rgba)
bob.point["spin"] = db.quat(rgba)
bob.corner["uv_offset"] = db.vec2(np.zeros((len(bob.corner), 2)))

for name in ["tint", "spin", "uv_offset"]:
    attribute = db.Attribute(bob.attributes[name])
    print(name, attribute.atype.name, attribute.domain.name)
```

    tint FLOAT_COLOR POINT
    spin QUATERNION POINT
    uv_offset FLOAT2 CORNER

Wrapping values that don’t fit the type, such as integers outside the range of `int8`, raises an [`AttributeMismatchError`](api/AttributeMismatchError.llms.md#databpy.AttributeMismatchError):

``` python
try:
    db.int8([1, 2, 1000])
except db.AttributeMismatchError as e:
    print(e)
```

    Values in the range [1, 1000] can't be stored in the `INT8` attribute, which stores int8 values in the range [-128, 127].

Storing a typed array over an existing attribute of another type raises a [`NamedAttributeError`](api/NamedAttributeError.llms.md#databpy.NamedAttributeError). databpy doesn’t convert the values:

``` python
try:
    bob.point["tint"] = db.quat(rgba)
except db.NamedAttributeError as e:
    print(e)
```

    Attribute being written to: `tint` of type `FLOAT_COLOR` does not match the type for the given data: `QUATERNION`

### Store one value for every element

A single value is stored for every element of the domain. The value can be a plain scalar, or a typed array of one value:

``` python
bob.point["weight"] = 1.0
bob.face["face_tint"] = db.color([1.0, 0.5, 0.0, 1.0])
bob.point["frame"] = db.mat4(np.eye(4))

print(bob.face["face_tint"][:2])
```

    AttributeArray 'face_tint' from Cube('Cube')(domain: FACE, shape: (2, 4), dtype: float32)
    [[1.  0.5 0.  1. ]
     [1.  0.5 0.  1. ]]

A plain list such as `[1, 0.5, 0, 1]` isn’t stored as a single value, as it could also be one value for each of 4 elements. Wrap a single vector, color or matrix in its typed array to store it on every element.

### Read typed data

databpy reads each attribute as the typed array for its type, so `bob["position"]` is a `db.vec3`. Every typed array is an [`AttributeArray`](api/AttributeArray.llms.md#databpy.AttributeArray), which writes changes back to Blender, as [Syncing with Blender](syncing.llms.md) explains:

``` python
position = bob["position"]
print(type(position).__name__, isinstance(position, db.AttributeArray))
```

    vec3 True

Index with a typed array after the name to check the attribute’s type. A different type raises a [`NamedAttributeError`](api/NamedAttributeError.llms.md#databpy.NamedAttributeError). The check works on every domain view, and as `atype=` for [`named_attribute()`](api/named_attribute.llms.md#databpy.named_attribute) and [`GeometrySet.named_attribute()`](api/GeometrySet.llms.md#databpy.GeometrySet.named_attribute):

``` python
position = bob.point["position", db.vec3]
tint = bob["tint", db.color]
values = db.named_attribute(bob.object, "position", atype=db.vec3)

try:
    bob["position", db.quat]
except db.NamedAttributeError as e:
    print(e)
```

    Attribute `position` is a `FLOAT_VECTOR` attribute, not `quat` (`QUATERNION`).

### Let type checkers see the type

The typed arrays are generic NumPy arrays, so type checkers such as `ty`, `pyright` and `mypy` know the dtype and shape of each one. The type of an attribute is only known once Blender is running, so a type checker only sees it when you state it as you read:

``` python
bob["position"]                              # AttributeArray[Any, Any]
bob["position", db.vec3]                     # vec3
bob.face["area", db.float32]                 # float32
db.named_attribute(obj, "x", atype=db.mat4)  # mat4
bob["position", db.vec3][:, 0]               # ndarray[..., dtype[float32]]
```

Editors use these types to complete NumPy methods and to catch mistakes, such as treating a matrix attribute as a vector.

## Store sRGB colors

Blender stores `FLOAT_COLOR` attributes as linear colors, which `db.color` reads and writes as they are. Colors from an image editor or a hex code are usually sRGB. [`db.srgb`](api/srgb.llms.md#databpy.srgb) is a typed array of sRGB colors for `FLOAT_COLOR` attributes. databpy converts its values to linear when you store them, and back to sRGB when you read the attribute as `db.srgb`. The stored attribute is the same as one stored with `db.color`, and alpha isn’t converted:

``` python
orange = np.tile([1.0, 0.5, 0.0, 1.0], (len(bob.point), 1))
bob.point["paint"] = db.srgb(orange)

print(bob.point["paint", db.srgb][0])  # sRGB, as it was stored
print(bob.point["paint"][0])  # linear, as Blender stores it
```

    AttributeArray 'paint' from Cube('Cube')(domain: POINT, shape: (4,), dtype: float32)
    [0.99999994 0.5        0.         1.        ]
    AttributeArray 'paint' from Cube('Cube')(domain: POINT, shape: (4,), dtype: float32)
    [1.         0.21404114 0.         1.        ]

`db.srgb` accepts hex color codes as `'#RRGGBB'`, `'#RRGGBBAA'`, or the short `'#RGB'` and `'#RGBA'`. Give one code for every element, or a list of codes. `db.color8` accepts hex codes too, as its bytes are also sRGB:

``` python
bob.point["highlight"] = db.srgb("#FF8000")
bob.point["palette"] = db.srgb(["#264653", "#2A9D8F", "#E9C46A", "#F4A261"] * 2)
bob.face["bytes"] = db.color8("#FF800080")

print(bob.face["bytes"][0])
```

    AttributeArray 'bytes' from Cube('Cube')(domain: FACE, shape: (4,), dtype: uint8)
    [255 128   0 128]

`db.srgb(bob.face["bytes"])` scales the bytes of a `db.color8` to sRGB floats in \[0, 1\].

An array read as `db.srgb` converts changes back to linear when it writes them to Blender. Math on a `db.srgb` array gives a `db.srgb` array, which databpy also converts when you store it. Math that mixes in a linear `db.color` gives a plain array, as the result is neither sRGB nor linear:

``` python
paint = bob.point["paint", db.srgb]
paint[:, :3] *= 0.5  # written back as linear
bob.point["dark_paint"] = paint * 0.5  # still sRGB, so converted when stored
```

Keep the following in mind when you work with sRGB colors:

- Each write converts every row it changed, so changing a column such as `paint[:, 0]` converts every color. The same change to a `db.color` is much faster.
- Read colors as sRGB with `bob["paint", db.srgb]`. `bob["paint"].view(db.srgb)` doesn’t convert the values, so it labels linear values as sRGB.
- A single row such as `paint[0]` is a plain `AttributeArray`, so storing it doesn’t convert it. Wrap it as `db.srgb(paint[0])` to store it as one sRGB color.

## Store plain NumPy arrays

You don’t have to use typed arrays. When you store a plain NumPy array, databpy infers the type from its dtype and shape. You can also give the type as `atype`, with Blender’s name for the type as a string or from the [`AttributeTypes`](api/AttributeTypes.llms.md#databpy.AttributeTypes) enum:

``` python
bob["temperature"] = np.random.rand(8)  # inferred as FLOAT
db.store_named_attribute(bob.object, np.random.rand(8, 4), "spin2", atype="QUATERNION")
db.store_named_attribute(
    bob.object, np.random.rand(8, 4), "spin3", atype=db.AttributeTypes.QUATERNION
)
```

    bpy.data.meshes['Cube'].attributes["spin3"]

[`guess_atype_from_array()`](api/attribute.guess_atype_from_array.llms.md#databpy.attribute.guess_atype_from_array) infers the type as the following table shows:

| Array | Inferred type |
|----|----|
| `(n,)` float / int / int8 / bool / str | `FLOAT` / `INT` / `INT8` / `BOOLEAN` / `STRING` |
| `(n, 2)` float / int16 / other int | `FLOAT2` / `INT16_2D` / `INT32_2D` |
| `(n, 3)` numeric | `FLOAT_VECTOR` |
| `(n, 4)` uint8 | `BYTE_COLOR` |
| `(n, 4)` other numeric | `FLOAT4` (`FLOAT_COLOR` before Blender 5.2) |
| `(n, 4, 4)` numeric | `FLOAT4X4` |

databpy never infers `FLOAT_COLOR` or `QUATERNION`, so use `db.color` and `db.quat` for them.

## Store text

`db.string` stores text, with one string for each element:

``` python
bob.point["name"] = db.string([f"point_{i}" for i in range(len(bob.point))])
```

    /tmp/ipykernel_3743/1214724840.py:1: UserWarning: String attributes can be read and written through the Python API but are not yet properly supported within Geometry Nodes. Support may change in future Blender / databpy versions.
      bob.point["name"] = db.string([f"point_{i}" for i in range(len(bob.point))])

> **WARNING:**
>
> You can read and write STRING attributes through the Python API, but Geometry Nodes doesn’t fully support them yet, so databpy warns when you use them. They are also much slower than numeric attributes, as Blender can’t transfer them in bulk.

## Handle errors

Every error that databpy raises inherits from [`DatabpyError`](api/DatabpyError.llms.md#databpy.DatabpyError). The attribute errors are:

- [`NamedAttributeError`](api/NamedAttributeError.llms.md#databpy.NamedAttributeError), for an invalid name, data of the wrong length for the domain, an attribute on a different domain from the domain view, or a type or domain that conflicts with an existing attribute or a typed array.
- [`AttributeNotFoundError`](api/AttributeNotFoundError.llms.md#databpy.AttributeNotFoundError), a `NamedAttributeError` for an attribute that doesn’t exist, such as `bob["missing"]`. It is also a `KeyError`.
- [`AttributeMismatchError`](api/AttributeMismatchError.llms.md#databpy.AttributeMismatchError), a `NamedAttributeError` for data of the wrong shape, or values that don’t fit the attribute’s type.
- [`LinkedObjectError`](api/LinkedObjectError.llms.md#databpy.LinkedObjectError), for an `AttributeArray` that can’t write back to Blender, because its object was removed or a file was loaded.

Wrapping data of the wrong shape in a typed array, such as `db.vec3(np.zeros(8))`, raises a `ValueError`.

The following example triggers some of these errors:

``` python
obj = bpy.data.objects["Cube"]
bob = db.BlenderObject(obj)

try:
    bob["nonexistent"]
except db.AttributeNotFoundError as e:
    print(f"Attribute not found: {e}")

try:
    bob.face["test"] = db.float32(np.random.rand(100))
except db.NamedAttributeError as e:
    print(f"Wrong length: {e}")

try:
    bob["position", db.color]
except db.NamedAttributeError as e:
    print(f"Wrong type: {e}")
```

    Attribute not found: The attribute 'nonexistent' does not exist on 'Cube'. Available attributes: ['.corner_edge', '.corner_vert', '.edge_verts', '.select_edge', '.select_poly', '.select_vert', '.uv_select_edge', '.uv_select_face', '.uv_select_vert', 'UVMap', 'area', 'bytes', 'crease_weight', 'dark_paint', 'face_tint', 'frame', 'highlight', 'name', 'normal_offset', 'offset', 'paint', 'palette', 'position', 'sharp_face', 'spin', 'spin2', 'spin3', 'temperature', 'tint', 'uv_offset', 'weight']
    Wrong length: Data size 100 (shape (100,)) does not match the required size 6 for domain `FACE` with 6 elements and dimensions (1,)
    Wrong type: Attribute `position` is a `FLOAT_VECTOR` attribute, not `color` (`FLOAT_COLOR`).

To handle every attribute error, catch `db.NamedAttributeError`. To handle every databpy error, catch `db.DatabpyError`.

`NamedAttributeError` also inherits from `AttributeError` for now. databpy 0.14.0 removes this, as `hasattr()` and `getattr()` silently swallow an `AttributeError`, so catch `NamedAttributeError` or `DatabpyError` instead.
