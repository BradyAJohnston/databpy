# store_named_attribute

``` python
store_named_attribute(obj, data, name, atype=None, domain=None, overwrite=True)
```

Write values to a named attribute on the object, creating it if needed.

## Parameters

| Name | Type | Description | Default |
|----|----|----|----|
| obj | `bpy`.[types](https://docs.blender.org/api/current/bpy.types.html#module-bpy.types).[Object](https://docs.blender.org/api/current/bpy.types.Object.html#bpy.types.Object) | The Blender object, with mesh, curves or point cloud data. | *required* |
| data | [npt](https://numpy.org/doc/stable/reference/typing.html#module-numpy.typing).[ArrayLike](https://numpy.org/doc/stable/reference/typing.html#numpy.typing.ArrayLike) | The attribute data, as a numpy array or anything convertible to one. | *required* |
| name | [str](https://docs.python.org/3/builtins/stdtypes.html#str) | The name of the attribute. | *required* |
| atype | [str](https://docs.python.org/3/builtins/stdtypes.html#str) or [AttributeTypes](../api/AttributeTypes.llms.md#databpy.AttributeTypes) or None | The attribute type to store the data as. If None, the type of an existing attribute is used, otherwise the type is inferred from data. | `None` |
| domain | [str](https://docs.python.org/3/builtins/stdtypes.html#str) or [AttributeDomains](../api/AttributeDomains.llms.md#databpy.AttributeDomains) or None | The domain of the attribute. If None, the domain of an existing attribute is used, otherwise ‘POINT’. | `None` |
| overwrite | [bool](https://docs.python.org/3/builtins/functions.html#bool) | Whether to write to an existing attribute with the same name, by default True. If False, a new attribute is created, which Blender gives a unique name such as `name.001`. | `True` |

## Returns

| Name | Type | Description |
|----|----|----|
|  | `bpy`.[types](https://docs.blender.org/api/current/bpy.types.html#module-bpy.types).[Attribute](https://docs.blender.org/api/current/bpy.types.Attribute.html#bpy.types.Attribute) | The created or modified attribute. |

## Raises

| Name | Type | Description |
|----|----|----|
|  | [ValueError](https://docs.python.org/3/builtins/exceptions.html#ValueError) | If atype or domain doesn’t match an available type or domain, no type can be inferred, or atype is FLOAT4 before Blender 5.2. |
|  | [NamedAttributeError](../api/NamedAttributeError.llms.md#databpy.NamedAttributeError) | If the object doesn’t hold attributes, the name is empty, the data size doesn’t match the domain, the atype or domain conflict with an existing attribute, or the attribute can’t be created on the domain. |
|  | [AttributeMismatchError](../api/AttributeMismatchError.llms.md#databpy.AttributeMismatchError) | If the values can’t be represented by the attribute’s type. |

## Examples

``` python
import bpy
import numpy as np
from databpy import store_named_attribute, list_attributes, named_attribute
obj = bpy.data.objects["Cube"]
print(f"{list_attributes(obj)=}")
```

    list_attributes(obj)=['.corner_edge', '.corner_vert', '.edge_verts', '.select_edge', '.select_poly', '.select_vert', '.uv_select_edge', '.uv_select_face', '.uv_select_vert', 'UVMap', 'position', 'sharp_face']

``` python
store_named_attribute(obj, np.arange(8), "test_attribute")
print(f"{list_attributes(obj)=}")
```

    list_attributes(obj)=['.corner_edge', '.corner_vert', '.edge_verts', '.select_edge', '.select_poly', '.select_vert', '.uv_select_edge', '.uv_select_face', '.uv_select_vert', 'UVMap', 'position', 'sharp_face', 'test_attribute']

``` python
named_attribute(obj, "test_attribute")
```

    array([0, 1, 2, 3, 4, 5, 6, 7], dtype=int32)
