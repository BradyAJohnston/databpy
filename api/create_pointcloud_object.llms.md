# create_pointcloud_object

``` python
create_pointcloud_object(positions=None, name='PointCloud', collection=None)
```

Create a new Blender point cloud object.

This function creates a point cloud by first creating a mesh with vertices at the specified positions, then converting it to a point cloud using Blender’s convert operator.

## Parameters

| Name | Type | Description | Default |
|----|----|----|----|
| positions | [np](https://numpy.org/doc/stable/reference/index.html#module-numpy).[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray) | The point positions as a numpy array with shape (N, 3). If None, creates an empty point cloud object. Defaults to None. | `None` |
| name | [str](https://docs.python.org/3/library/stdtypes.html#str) | The name of the object. Defaults to ‘PointCloud’. | `'PointCloud'` |
| collection | `bpy`.[types](https://docs.blender.org/api/current/bpy.types.html#module-bpy.types).[Collection](https://docs.blender.org/api/current/bpy.types.Collection.html#bpy.types.Collection) | The collection to link the object to. Defaults to None. | `None` |

## Returns

| Name | Type | Description |
|----|----|----|
|  | [Object](https://docs.blender.org/api/current/bpy.types.Object.html#bpy.types.Object) | The created point cloud object. |

## Examples

``` python
import numpy as np
from databpy import create_pointcloud_object

# Create point cloud with 100 random points
positions = np.random.random((100, 3))
pc_obj = create_pointcloud_object(positions, name="MyPC")
print(len(pc_obj.data.points))  # 100
```

## Notes

This function works by creating a temporary mesh and converting it to a point cloud using `bpy.ops.object.convert(target='POINTCLOUD')`.
