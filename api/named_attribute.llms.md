# named_attribute

``` python
named_attribute(obj, name='position', evaluate=False, *, atype=None)
```

Read the values of a named attribute into a numpy array.

## Parameters

| Name | Type | Description | Default |
|----|----|----|----|
| obj | `bpy`.[types](https://docs.blender.org/api/current/bpy.types.html#module-bpy.types).[Object](https://docs.blender.org/api/current/bpy.types.Object.html#bpy.types.Object) | The Blender object. | *required* |
| name | [str](https://docs.python.org/3/builtins/stdtypes.html#str) | The name of the attribute, by default ‘position’. | `'position'` |
| evaluate | [bool](https://docs.python.org/3/builtins/functions.html#bool) | Whether to evaluate modifiers before reading, by default False. | `False` |
| atype | [type](https://docs.python.org/3/builtins/functions.html#type)\[[AttributeArray](../api/AttributeArray.llms.md#databpy.AttributeArray)\] or None | The typed array class the attribute is expected to be, such as `vec3`. The values are returned as that class, which type checkers also see. | `None` |

## Returns

| Name | Type | Description |
|----|----|----|
|  | [np](https://numpy.org/doc/stable/reference/index.html#module-numpy).[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray) | The attribute data as a numpy array, or an array of `atype` if given. |

## Raises

| Name | Type | Description |
|----|----|----|
|  | [AttributeNotFoundError](../api/AttributeNotFoundError.llms.md#databpy.AttributeNotFoundError) | If the named attribute does not exist on the object. |
|  | [NamedAttributeError](../api/NamedAttributeError.llms.md#databpy.NamedAttributeError) | If the attribute’s type doesn’t match `atype`. |
|  | [TypeError](https://docs.python.org/3/builtins/exceptions.html#TypeError) | If `obj` isn’t an object, or its data isn’t a mesh, curves, point cloud or grease pencil. |

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
