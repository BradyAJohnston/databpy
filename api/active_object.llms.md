# active_object

``` python
active_object(context=None)
```

Return the active object, raising an error if there is none.

## Parameters

| Name | Type | Description | Default |
|----|----|----|----|
| context | `bpy`.[types](https://docs.blender.org/api/current/bpy.types.html#module-bpy.types).[Context](https://docs.blender.org/api/current/bpy.types.Context.html#bpy.types.Context) \| None | The context to read the active object from. Defaults to `bpy.context`. | `None` |

## Returns

| Name | Type | Description |
|----|----|----|
|  | `bpy`.[types](https://docs.blender.org/api/current/bpy.types.html#module-bpy.types).[Object](https://docs.blender.org/api/current/bpy.types.Object.html#bpy.types.Object) | The active object. |

## Raises

| Name | Type | Description |
|----|----|----|
|  | [ValueError](https://docs.python.org/3/builtins/exceptions.html#ValueError) | If the context has no active object. |
