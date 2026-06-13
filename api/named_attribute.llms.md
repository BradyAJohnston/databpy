# named_attribute

``` python
named_attribute(obj, name='position', evaluate=False)
```

Get the named attribute data from the object.

## Parameters

| Name | Type | Description | Default |
|----|----|----|----|
| obj | `bpy`.[types](https://docs.blender.org/api/current/bpy.types.html#module-bpy.types).[Object](https://docs.blender.org/api/current/bpy.types.Object.html#bpy.types.Object) | The Blender object. | *required* |
| name | [str](https://docs.python.org/3/library/stdtypes.html#str) | The name of the attribute, by default ‘position’. | `'position'` |
| evaluate | [bool](https://docs.python.org/3/library/functions.html#bool) | Whether to evaluate modifiers before reading, by default False. | `False` |

## Returns

| Name | Type | Description |
|----|----|----|
|  | [np](https://numpy.org/doc/stable/reference/index.html#module-numpy).[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray) | The attribute data as a numpy array. |

## Raises

| Name | Type | Description |
|----|----|----|
|  | [AttributeError](https://docs.python.org/3/library/exceptions.html#AttributeError) | If the named attribute does not exist on the mesh. |

## Examples

``` python
import bpy
from databpy import named_attribute, list_attributes
obj = bpy.data.objects["Cube"]
print(f"{list_attributes(obj)=}")
```

    list_attributes(obj)=['.corner_edge', '.corner_vert', '.edge_verts', '.select_edge', '.select_poly', '.select_vert', '.uv_select_edge', '.uv_select_face', '.uv_select_vert', 'UVMap', 'position', 'sharp_face']

``` python
named_attribute(obj, "position")
```

    array([[ 1.,  1.,  1.],
           [ 1.,  1., -1.],
           [ 1., -1.,  1.],
           [ 1., -1., -1.],
           [-1.,  1.,  1.],
           [-1.,  1., -1.],
           [-1., -1.,  1.],
           [-1., -1., -1.]], dtype=float32)
