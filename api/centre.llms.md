# centre

``` python
centre(position, weight=None)
```

Calculate the weighted centroid of the vectors.

## Parameters

| Name | Type | Description | Default |
|----|----|----|----|
| position | [np](https://numpy.org/doc/stable/reference/index.html#module-numpy).[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray) | Array of position vectors. | *required* |
| weight | [np](https://numpy.org/doc/stable/reference/index.html#module-numpy).[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray) \| None | Array of weights for each position. Default is None. | `None` |

## Returns

| Name | Type | Description |
|----|----|----|
|  | [np](https://numpy.org/doc/stable/reference/index.html#module-numpy).[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray) | The weighted centroid of the input vectors. |
