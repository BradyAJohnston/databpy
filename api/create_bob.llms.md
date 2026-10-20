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
| vertices | `ndarray` or None | Array of vertex coordinates with shape (N, 3). Default is None. | `None` |
| edges | `ndarray` or None | Vertex indices of each edge, with shape (M, 2). Default is None. | `None` |
| faces | `ndarray` or None | Vertex indices of each face. Default is None. | `None` |
| name | [str](https://docs.python.org/3/builtins/stdtypes.html#str) | Name of the created object. Default is “NewObject”. | `'NewObject'` |
| collection | `bpy`.[types](https://docs.blender.org/api/current/bpy.types.html#module-bpy.types).[Collection](https://docs.blender.org/api/current/bpy.types.Collection.html#bpy.types.Collection) or None | Blender collection to link the object to. None links it to a collection named “Collection”, created if needed. Default is None. | `None` |
| uuid | [str](https://docs.python.org/3/builtins/stdtypes.html#str) or None | The UUID to store on the object and use for the BlenderObject. None generates a new UUID. Default is None. | `None` |

## Returns

| Name | Type | Description |
|----|----|----|
|  | [BlenderObject](../api/BlenderObject.llms.md#databpy.BlenderObject) | A wrapped Blender mesh object. |

## Raises

| Name | Type | Description |
|----|----|----|
|  | [ValueError](https://docs.python.org/3/builtins/exceptions.html#ValueError) | If `vertices` doesn’t have the shape (N, 3), an edge doesn’t have exactly 2 vertex indices, or an index is outside of the vertices. |
|  | [TypeError](https://docs.python.org/3/builtins/exceptions.html#TypeError) | If edge or face indices aren’t integers. |
