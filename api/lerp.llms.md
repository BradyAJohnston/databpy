# lerp

``` python
lerp(a, b, t=0.5)
```

Linearly interpolate between two values.

## Parameters

| Name | Type | Description | Default |
|----|----|----|----|
| a | [npt](https://numpy.org/doc/stable/reference/typing.html#module-numpy.typing).[ArrayLike](https://numpy.org/doc/stable/reference/typing.html#numpy.typing.ArrayLike) | The starting value(s). | *required* |
| b | [npt](https://numpy.org/doc/stable/reference/typing.html#module-numpy.typing).[ArrayLike](https://numpy.org/doc/stable/reference/typing.html#numpy.typing.ArrayLike) | The ending value(s). | *required* |
| t | [float](https://docs.python.org/3/builtins/functions.html#float) \| [npt](https://numpy.org/doc/stable/reference/typing.html#module-numpy.typing).[ArrayLike](https://numpy.org/doc/stable/reference/typing.html#numpy.typing.ArrayLike) | The interpolation parameter. Default is 0.5. | `0.5` |

## Returns

| Name | Type | Description |
|----|----|----|
|  | [np](https://numpy.org/doc/stable/reference/index.html#module-numpy).[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray) | The interpolated value(s). |

## Notes

This function performs linear interpolation between `a` and `b` using the interpolation parameter `t` such that the result lies between `a` and `b`.

## Examples

``` python
from databpy.utils import lerp
lerp(1, 2, 0.5)
lerp(3, 7, 0.2)
lerp([1, 2, 3], [4, 5, 6], 0.5)
```

    array([2.5, 3.5, 4.5])
