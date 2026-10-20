# create_collection

``` python
create_collection(name='NewCollection', parent=None)
```

Create a new Blender collection or get an existing one.

A collection that doesn’t exist yet is created and linked to the active scene’s collection. An existing collection is returned without changing where it is linked, unless a parent is given.

## Parameters

| Name | Type | Description | Default |
|----|----|----|----|
| name | [str](https://docs.python.org/3/builtins/stdtypes.html#str) | The name of the collection to create or get. Default is “NewCollection”. | `'NewCollection'` |
| parent | [Collection](https://docs.blender.org/api/current/bpy.types.Collection.html#bpy.types.Collection) or [str](https://docs.python.org/3/builtins/stdtypes.html#str) or None | The collection to link the collection into, which also unlinks it from the scene’s collection. A string is the name of the parent collection, which is created and linked to the scene if it doesn’t exist. Default is None, which leaves the collection where it is. | `None` |

## Returns

| Name | Type | Description |
|----|----|----|
|  | [Collection](https://docs.blender.org/api/current/bpy.types.Collection.html#bpy.types.Collection) | The created or existing collection. |

## Raises

| Name | Type | Description |
|----|----|----|
|  | [TypeError](https://docs.python.org/3/builtins/exceptions.html#TypeError) | If `parent` is not a Collection, string or None. |
