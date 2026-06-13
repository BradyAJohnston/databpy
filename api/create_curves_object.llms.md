# create_curves_object

``` python
create_curves_object(
    positions=None,
    curve_sizes=None,
    name='Curves',
    collection=None,
)
```

Create a new Blender curves object (new Curves type, not legacy Curve).

## Parameters

| Name | Type | Description | Default |
|----|----|----|----|
| positions | [np](https://numpy.org/doc/stable/reference/index.html#module-numpy).[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray) | The control point positions as a numpy array with shape (N, 3). If None, creates an empty curves object. Defaults to None. | `None` |
| curve_sizes | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[int](https://docs.python.org/3/library/functions.html#int)\] \| [np](https://numpy.org/doc/stable/reference/index.html#module-numpy).[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray) | Number of points in each curve. For example, \[4, 5, 6\] creates 3 curves with 4, 5, and 6 control points respectively. Total must equal len(positions). If None, creates an empty curves object. Defaults to None. | `None` |
| name | [str](https://docs.python.org/3/library/stdtypes.html#str) | The name of the object. Defaults to ‘Curves’. | `'Curves'` |
| collection | `bpy`.[types](https://docs.blender.org/api/current/bpy.types.html#module-bpy.types).[Collection](https://docs.blender.org/api/current/bpy.types.Collection.html#bpy.types.Collection) | The collection to link the object to. Defaults to None. | `None` |

## Returns

| Name | Type | Description |
|----|----|----|
|  | [Object](https://docs.blender.org/api/current/bpy.types.Object.html#bpy.types.Object) | The created curves object. |

## Raises

| Name | Type | Description |
|----|----|----|
|  | [ValueError](https://docs.python.org/3/library/exceptions.html#ValueError) | If positions and curve_sizes lengths don’t match. |

## Examples

``` python
import numpy as np
from databpy import create_curves_object

# Create 2 curves with 3 and 4 points
positions = np.random.random((7, 3))
curves_obj = create_curves_object(positions, [3, 4])
```
