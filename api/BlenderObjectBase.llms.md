# BlenderObjectBase

``` python
BlenderObjectBase(obj=None)
```

Minimal base class for Blender objects with name and object access.

This provides a minimal set of functionality to persistently track a an object in Blender’s database, providing access to it’s name property and also the object itself. Referencing an object in the database directly can lead to ReferenceErrors as Blender can *without warning* alter the database and thus the Object’s place in memory.

To get around this BlenderObjectBase always looks up via the name attribute and double checks with the `uuid` attribute to ensure the correct object is being returned. If there is a mismatch the entite database will be searched for an object with a uuid that matches and if none is found a LinkedObjectError will be raised.

Blender *internally* uses it’s own UUID / reference system but this is currently (and frustratingly) not available to us via the Python API.

## Attributes

| Name | Type | Description |
|----|----|----|
| object | `bpy`.[types](https://docs.blender.org/api/current/bpy.types.html#module-bpy.types).[Object](https://docs.blender.org/api/current/bpy.types.Object.html#bpy.types.Object) | The wrapped Blender object. |
| uuid | [str](https://docs.python.org/3/library/stdtypes.html#str) | Unique identifier for this object instance. |
| name | [str](https://docs.python.org/3/library/stdtypes.html#str) | Name of the Blender object. |
