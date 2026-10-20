# BlenderObjectBase

``` python
BlenderObjectBase(obj=None)
```

Minimal base class for Blender objects with name and object access.

Tracks an object in Blender’s database and gives access to the object and its name. A direct reference to an object can raise `ReferenceError`, as Blender can reallocate data-blocks without warning, so the object is tracked in two ways:

- Within a session, by the object’s `session_uid`, which stays the same across renames and internal reallocations. Duplicates of the object get a new `session_uid`, so they are never mistaken for the original. If the object is removed, accessing it raises a `LinkedObjectError`.
- Across sessions (after loading a .blend file, or in a new Python process), by a persistent `uuid` stored on the object as a custom property. On first access in a new session the object is found by its `uuid` and then tracked by its new `session_uid`.

## Attributes

| Name | Type | Description |
|----|----|----|
| object | `bpy`.[types](https://docs.blender.org/api/current/bpy.types.html#module-bpy.types).[Object](https://docs.blender.org/api/current/bpy.types.Object.html#bpy.types.Object) | The wrapped Blender object. |
| uuid | [str](https://docs.python.org/3/builtins/stdtypes.html#str) | Unique identifier for this object instance. |
| name | [str](https://docs.python.org/3/builtins/stdtypes.html#str) | Name of the Blender object. |
