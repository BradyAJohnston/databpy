# create_object

``` python
create_object(
    vertices=None,
    edges=None,
    faces=None,
    name='NewObject',
    collection=None,
)
```

Create a new Blender mesh object.

## Parameters

| Name | Type | Description | Default |
|----|----|----|----|
| vertices | [np](https://numpy.org/doc/stable/reference/index.html#module-numpy).[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray) | The vertices as a numpy array. Defaults to None. | `None` |
| edges | [np](https://numpy.org/doc/stable/reference/index.html#module-numpy).[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray) | The edges as a numpy array. Defaults to None. | `None` |
| faces | [np](https://numpy.org/doc/stable/reference/index.html#module-numpy).[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray) | The faces as a numpy array. Defaults to None. | `None` |
| name | [str](https://docs.python.org/3/library/stdtypes.html#str) | The name of the object. Defaults to ‘NewObject’. | `'NewObject'` |
| collection | `bpy`.[types](https://docs.blender.org/api/current/bpy.types.html#module-bpy.types).[Collection](https://docs.blender.org/api/current/bpy.types.Collection.html#bpy.types.Collection) | The collection to link the object to. Defaults to None. | `None` |

## Returns

| Name | Type | Description |
|----|----|----|
|  | [Object](https://docs.blender.org/api/current/bpy.types.Object.html#bpy.types.Object) | The created mesh object. |
