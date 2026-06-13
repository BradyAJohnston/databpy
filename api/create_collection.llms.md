# create_collection

``` python
create_collection(name='NewCollection', parent=None)
```

Create a new Blender collection or retrieve an existing one.

## Parameters

| Name | Type | Description | Default |
|----|----|----|----|
| name | [str](https://docs.python.org/3/library/stdtypes.html#str) | The name of the collection to create or retrieve. Default is “NewCollection”. | `'NewCollection'` |
| parent | [Collection](https://docs.blender.org/api/current/bpy.types.Collection.html#bpy.types.Collection) or [str](https://docs.python.org/3/library/stdtypes.html#str) or None | The parent collection to link the new collection to. If a string is provided, it will be used to find an existing collection by name. If None, the new collection will be linked to the scene’s root collection. Default is None. | `None` |

## Returns

| Name | Type | Description |
|----|----|----|
|  | [Collection](https://docs.blender.org/api/current/bpy.types.Collection.html#bpy.types.Collection) | The created or retrieved Blender collection. |

## Raises

| Name | Type | Description |
|----|----|----|
|  | [TypeError](https://docs.python.org/3/library/exceptions.html#TypeError) | If the parent parameter is not a Collection, string or None. |
|  | [KeyError](https://docs.python.org/3/library/exceptions.html#KeyError) | If the parent collection name provided does not exist in bpy.data.collections. |
