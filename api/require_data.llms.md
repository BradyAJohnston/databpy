# require_data

``` python
require_data(obj, data_type)
```

Return the object’s data-block, checked to be of the given type.

`Object.data` can be any of Blender’s data-block types (or None), so this helper narrows it to the expected type with a proper runtime check.

## Parameters

| Name | Type | Description | Default |
|----|----|----|----|
| obj | `bpy`.[types](https://docs.blender.org/api/current/bpy.types.html#module-bpy.types).[Object](https://docs.blender.org/api/current/bpy.types.Object.html#bpy.types.Object) | The object to get the data-block from. | *required* |
| data_type | [type](https://docs.python.org/3/builtins/functions.html#type)\[`DataBlockT`\] | The expected type of the data-block (e.g. `bpy.types.Mesh`). | *required* |

## Returns

| Name | Type | Description |
|----|----|----|
|  | `DataBlockT` | The object’s data-block, guaranteed to be of the given type. |

## Raises

| Name | Type | Description |
|----|----|----|
|  | [TypeError](https://docs.python.org/3/builtins/exceptions.html#TypeError) | If the object’s data is not of the expected type. |
