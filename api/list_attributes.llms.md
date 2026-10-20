# list_attributes

``` python
list_attributes(obj, evaluate=False, drop_hidden=False)
```

List the names of the attributes on an object, sorted alphabetically.

## Parameters

| Name | Type | Description | Default |
|----|----|----|----|
| obj | `bpy`.[types](https://docs.blender.org/api/current/bpy.types.html#module-bpy.types).[Object](https://docs.blender.org/api/current/bpy.types.Object.html#bpy.types.Object) | The Blender object, with mesh, curves or point cloud data. | *required* |
| evaluate | [bool](https://docs.python.org/3/builtins/functions.html#bool) | Whether to list the attributes after evaluating modifiers, by default False. | `False` |
| drop_hidden | [bool](https://docs.python.org/3/builtins/functions.html#bool) | Whether to leave out hidden attributes, whose names start with `.`, by default False. | `False` |

## Returns

| Name | Type | Description |
|----|----|----|
|  | [list](https://docs.python.org/3/builtins/stdtypes.html#list)\[[str](https://docs.python.org/3/builtins/stdtypes.html#str)\] | The attribute names. |

## Raises

| Name | Type | Description |
|----|----|----|
|  | [TypeError](https://docs.python.org/3/builtins/exceptions.html#TypeError) | If the object’s data isn’t a mesh, curves or point cloud. |
