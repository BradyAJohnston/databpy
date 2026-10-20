# LinkedObjectError

``` python
LinkedObjectError(message)
```

Error raised when a wrapper can no longer find the Blender object it is linked to.

Raised when the object of a `BlenderObject` or `AttributeArray` has been removed, or an `AttributeArray` is synced after a file was loaded.

## Parameters

| Name | Type | Description | Default |
|----|----|----|----|
| message | [str](https://docs.python.org/3/builtins/stdtypes.html#str) | The error message describing why the linked object is missing or invalid. | *required* |

## Attributes

| Name | Type | Description |
|----|----|----|
| message | [str](https://docs.python.org/3/builtins/stdtypes.html#str) | The error message that was passed. |
