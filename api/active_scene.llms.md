# active_scene

``` python
active_scene(context=None)
```

Return the active scene, raising an error if there is none.

## Parameters

| Name | Type | Description | Default |
|----|----|----|----|
| context | `bpy`.[types](https://docs.blender.org/api/current/bpy.types.html#module-bpy.types).[Context](https://docs.blender.org/api/current/bpy.types.Context.html#bpy.types.Context) \| None | The context to read the scene from. Defaults to `bpy.context`. | `None` |

## Returns

| Name | Type | Description |
|----|----|----|
|  | `bpy`.[types](https://docs.blender.org/api/current/bpy.types.html#module-bpy.types).[Scene](https://docs.blender.org/api/current/bpy.types.Scene.html#bpy.types.Scene) | The active scene. |

## Raises

| Name | Type | Description |
|----|----|----|
|  | [ValueError](https://docs.python.org/3/builtins/exceptions.html#ValueError) | If the context has no active scene. |
