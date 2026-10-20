# evaluate_object

``` python
evaluate_object(obj, context=None)
```

Return the object with its modifiers evaluated.

## Parameters

| Name | Type | Description | Default |
|----|----|----|----|
| obj | `bpy`.[types](https://docs.blender.org/api/current/bpy.types.html#module-bpy.types).[Object](https://docs.blender.org/api/current/bpy.types.Object.html#bpy.types.Object) | The Blender object to evaluate. | *required* |
| context | `bpy`.[types](https://docs.blender.org/api/current/bpy.types.html#module-bpy.types).[Context](https://docs.blender.org/api/current/bpy.types.Context.html#bpy.types.Context) \| None | The Blender context to use for evaluation, by default None | `None` |

## Returns

| Name | Type | Description |
|----|----|----|
|  | `bpy`.[types](https://docs.blender.org/api/current/bpy.types.html#module-bpy.types).[Object](https://docs.blender.org/api/current/bpy.types.Object.html#bpy.types.Object) | The evaluated object with modifiers applied. |

## Raises

| Name | Type | Description |
|----|----|----|
|  | [TypeError](https://docs.python.org/3/builtins/exceptions.html#TypeError) | If `obj` isn’t an object, or its data isn’t a mesh, curves or point cloud. |

## Notes

The object is tagged for an update, then read from the evaluated depsgraph of `context`, or of `bpy.context` if no context is given.

## Examples

``` python
import bpy
from databpy import evaluate_object
obj = bpy.data.objects['Cube']
evaluated_obj = evaluate_object(obj)
```
