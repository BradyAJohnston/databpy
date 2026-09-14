# require

``` python
require(value, message='Expected a value but got None')
```

Return the given value, raising an error if it is None.

Many Blender API accessors are typed as returning `SomeType | None`. This helper narrows such values to their non-None type, raising a clear error instead of an `AttributeError` further down the line.

## Parameters

| Name | Type | Description | Default |
|----|----|----|----|
| value | `T` \| None | The possibly-None value to check. | *required* |
| message | [str](https://docs.python.org/3/builtins/stdtypes.html#str) | The error message to raise if the value is None. | `'Expected a value but got None'` |

## Returns

| Name | Type | Description                           |
|------|------|---------------------------------------|
|      | `T`  | The value, guaranteed not to be None. |

## Raises

| Name | Type | Description |
|----|----|----|
|  | [ValueError](https://docs.python.org/3/builtins/exceptions.html#ValueError) | If the value is None. |
