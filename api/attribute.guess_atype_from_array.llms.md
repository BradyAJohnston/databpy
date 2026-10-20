# attribute.guess_atype_from_array

``` python
attribute.guess_atype_from_array(array)
```

Infer the attribute type for an array from its shape and dtype.

- `(n,)` or `(n, 1)`: bool to BOOLEAN, int8 to INT8, other integers to INT, floats to FLOAT, and strings to STRING. Unsigned integers map to INT, as their values may not fit INT8.
- `(n, 2)`: int16 to INT16_2D, other integers to INT32_2D, and floats to FLOAT2.
- `(n, 3)`: any numeric dtype to FLOAT_VECTOR.
- `(n, 4)`: uint8 to BYTE_COLOR, and other numeric dtypes to FLOAT4. Before Blender 5.2, which has no FLOAT4, they map to FLOAT_COLOR.
- `(n, 4, 4)`: any numeric dtype to FLOAT4X4.

FLOAT_COLOR and QUATERNION are never inferred, and must be passed as `atype`.

## Parameters

| Name | Type | Description | Default |
|----|----|----|----|
| array | [np](https://numpy.org/doc/stable/reference/index.html#module-numpy).[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray) | Input numpy array to analyze. | *required* |

## Returns

| Name | Type | Description |
|----|----|----|
|  | [AttributeTypes](../api/AttributeTypes.llms.md#databpy.AttributeTypes) | The inferred attribute type enum value. |

## Raises

| Name | Type | Description |
|----|----|----|
|  | [TypeError](https://docs.python.org/3/builtins/exceptions.html#TypeError) | If input is not a numpy array. |
|  | [ValueError](https://docs.python.org/3/builtins/exceptions.html#ValueError) | If the array has no dimensions, or no attribute type matches its shape and dtype. |

## Examples

``` python
>>> print(guess_atype_from_array(np.array([1.0, 2.0, 3.0], dtype=np.float32)))
AttributeTypes.FLOAT
>>> print(guess_atype_from_array(np.array([[1, 2], [3, 4]], dtype=np.int32)))
AttributeTypes.INT32_2D
>>> print(guess_atype_from_array(np.array([[255, 0, 0, 255]], dtype=np.uint8)))
AttributeTypes.BYTE_COLOR
```
