# create_bob

``` python
create_bob(
    vertices=None,
    edges=None,
    faces=None,
    name='NewObject',
    collection=None,
    uuid=None,
)
```

Create a BlenderObject wrapper around a new Blender mesh object.

## Parameters

| Name | Type | Description | Default |
|----|----|----|----|
| vertices | `ndarray` or None | Array of vertex coordinates. Default is None. | `None` |
| edges | `ndarray` or None | Array of edge indices. Default is None. | `None` |
| faces | `ndarray` or None | Array of face indices. Default is None. | `None` |
| name | [str](https://docs.python.org/3/library/stdtypes.html#str) | Name of the created object. Default is “NewObject”. | `'NewObject'` |
| collection | `bpy`.[types](https://docs.blender.org/api/current/bpy.types.html#module-bpy.types).[Collection](https://docs.blender.org/api/current/bpy.types.Collection.html#bpy.types.Collection) or None | Blender collection to link the object to. Default is None. | `None` |
| uuid | [str](https://docs.python.org/3/library/stdtypes.html#str) or None | Directly set the UUID on the resulting BlenderObject. Default is None. | `None` |

## Returns

| Name | Type | Description |
|----|----|----|
|  | [BlenderObject](../api/BlenderObject.llms.md#databpy.BlenderObject) | A wrapped Blender mesh object. |
