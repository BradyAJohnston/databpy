# evaluate_object

``` python
evaluate_object(obj, context=None)
```

Return an object which has the modifiers evaluated.

## Parameters

| Name | Type | Description | Default |
|----|----|----|----|
| obj | `bpy`.[types](https://docs.blender.org/api/current/bpy.types.html#module-bpy.types).[Object](https://docs.blender.org/api/current/bpy.types.Object.html#bpy.types.Object) | The Blender object to evaluate. | *required* |
| context | `bpy`.[types](https://docs.blender.org/api/current/bpy.types.html#module-bpy.types).[Context](https://docs.blender.org/api/current/bpy.types.Context.html#bpy.types.Context) \| None | The Blender context to use for evaluation, by default None | `None` |

## Returns

| Name | Type | Description |
|----|----|----|
|  | `bpy`.[types](https://docs.blender.org/api/current/bpy.types.html#module-bpy.types).[Object](https://docs.blender.org/api/current/bpy.types.Object.html#bpy.types.Object) | The evaluated object with modifiers applied. |

## Notes

This function evaluates the object’s modifiers using the current depsgraph. If no context is provided, it uses the current bpy.context.

## Examples

``` python
import bpy
from databpy import evaluate_object
obj = bpy.data.objects['Cube']
evaluated_obj = evaluate_object(obj)
```
