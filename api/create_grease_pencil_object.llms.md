# create_grease_pencil_object

``` python
create_grease_pencil_object(layers=None, name='GreasePencil', collection=None)
```

Create a new Blender grease pencil object.

Each layer gets one drawing on the scene’s current frame, holding its strokes. The drawing is only shown from that frame onwards, so a layer created on frame 10 has no drawing on frame 1. A layer with no strokes gets an empty drawing.

## Parameters

| Name | Type | Description | Default |
|----|----|----|----|
| layers | [Mapping](https://docs.python.org/3/library/collections.abc.html#collections.abc.Mapping)\[[str](https://docs.python.org/3/builtins/stdtypes.html#str), [tuple](https://docs.python.org/3/builtins/stdtypes.html#tuple)\[[np](https://numpy.org/doc/stable/reference/index.html#module-numpy).[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray), [list](https://docs.python.org/3/builtins/stdtypes.html#list)\[[int](https://docs.python.org/3/builtins/functions.html#int)\] \| [np](https://numpy.org/doc/stable/reference/index.html#module-numpy).[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray)\]\] | The layers to create, mapping each layer’s name to the positions of its points with shape (N, 3) and the number of points in each stroke. If None, creates an empty grease pencil object. Defaults to None. | `None` |
| name | [str](https://docs.python.org/3/builtins/stdtypes.html#str) | The name of the object. Defaults to ‘GreasePencil’. | `'GreasePencil'` |
| collection | `bpy`.[types](https://docs.blender.org/api/current/bpy.types.html#module-bpy.types).[Collection](https://docs.blender.org/api/current/bpy.types.Collection.html#bpy.types.Collection) | The collection to link the object to. Defaults to None, which links it to a collection named “Collection”, created if needed. | `None` |

## Returns

| Name | Type | Description |
|----|----|----|
|  | [Object](https://docs.blender.org/api/current/bpy.types.Object.html#bpy.types.Object) | The created grease pencil object. |

## Raises

| Name | Type | Description |
|----|----|----|
|  | [ValueError](https://docs.python.org/3/builtins/exceptions.html#ValueError) | If the positions of a layer don’t have shape (N, 3), a stroke has fewer than 1 point, or the stroke sizes of a layer don’t add up to the number of its positions. Every layer is checked before anything is created. |

## Examples

``` python
import numpy as np
from databpy import create_grease_pencil_object

# Create two layers, with 2 strokes and 1 stroke
gp_obj = create_grease_pencil_object(
    {
        "Lines": (np.random.random((7, 3)), [3, 4]),
        "Outline": (np.random.random((5, 3)), [5]),
    }
)
```
