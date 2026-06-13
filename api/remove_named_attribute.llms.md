# remove_named_attribute

``` python
remove_named_attribute(obj, name)
```

Remove a named attribute from an object.

## Parameters

| Name | Type | Description | Default |
|----|----|----|----|
| obj | `bpy`.[types](https://docs.blender.org/api/current/bpy.types.html#module-bpy.types).[Object](https://docs.blender.org/api/current/bpy.types.Object.html#bpy.types.Object) | The Blender object. | *required* |
| name | [str](https://docs.python.org/3/library/stdtypes.html#str) | Name of the attribute to remove. | *required* |

## Raises

| Name | Type | Description |
|----|----|----|
|  | [AttributeError](https://docs.python.org/3/library/exceptions.html#AttributeError) | If the named attribute does not exist on the mesh. |

## Examples

``` python
import bpy
import numpy as np
from databpy import remove_named_attribute, list_attributes, store_named_attribute
obj = bpy.data.objects["Cube"]
store_named_attribute(obj, np.random.rand(8, 3), "random_numbers")
print(f"{list_attributes(obj)=}")
```

    list_attributes(obj)=['.corner_edge', '.corner_vert', '.edge_verts', '.select_edge', '.select_poly', '.select_vert', '.uv_select_edge', '.uv_select_face', '.uv_select_vert', 'UVMap', 'position', 'random_numbers', 'sharp_face']

``` python
remove_named_attribute(obj, "random_numbers")
print(f"{list_attributes(obj)=}")
```

    list_attributes(obj)=['.corner_edge', '.corner_vert', '.edge_verts', '.select_edge', '.select_poly', '.select_vert', '.uv_select_edge', '.uv_select_face', '.uv_select_vert', 'UVMap', 'position', 'sharp_face']
