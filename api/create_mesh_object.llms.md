# create_mesh_object

``` python
create_mesh_object(
    vertices=None,
    edges=None,
    faces=None,
    name='Mesh',
    collection=None,
)
```

Create a new Blender mesh object.

## Parameters

| Name | Type | Description | Default |
|----|----|----|----|
| vertices | [np](https://numpy.org/doc/stable/reference/index.html#module-numpy).[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray) | The vertices as a numpy array with shape (N, 3). Defaults to None. | `None` |
| edges | [np](https://numpy.org/doc/stable/reference/index.html#module-numpy).[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray) | Vertex indices of each edge, with shape (M, 2). Defaults to None. | `None` |
| faces | [np](https://numpy.org/doc/stable/reference/index.html#module-numpy).[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray) | Vertex indices of each face. Faces with different numbers of vertices can be given as a list of lists. Defaults to None. | `None` |
| name | [str](https://docs.python.org/3/builtins/stdtypes.html#str) | The name of the object. Defaults to ‘Mesh’. | `'Mesh'` |
| collection | `bpy`.[types](https://docs.blender.org/api/current/bpy.types.html#module-bpy.types).[Collection](https://docs.blender.org/api/current/bpy.types.Collection.html#bpy.types.Collection) | The collection to link the object to. Defaults to None, which links it to a collection named “Collection”, created if needed. | `None` |

## Returns

| Name | Type | Description |
|----|----|----|
|  | [Object](https://docs.blender.org/api/current/bpy.types.Object.html#bpy.types.Object) | The created mesh object. |

## Raises

| Name | Type | Description |
|----|----|----|
|  | [ValueError](https://docs.python.org/3/builtins/exceptions.html#ValueError) | If `vertices` doesn’t have the shape (N, 3), an edge doesn’t have exactly 2 vertex indices, or an index is outside of the vertices. |
|  | [TypeError](https://docs.python.org/3/builtins/exceptions.html#TypeError) | If edge or face indices aren’t integers. |
