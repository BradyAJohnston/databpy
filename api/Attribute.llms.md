# Attribute

``` python
Attribute(attribute)
```

Low-level wrapper around a Blender attribute with explicit reads and writes.

Values are only read by `as_array` and only written by `from_array`. Use this class to control when values are transferred, for example to apply several whole-array operations with a single write, or to inspect an attribute’s type, domain and shape without reading its values.

For automatic syncing, use `AttributeArray`, a numpy array subclass that writes changes back to Blender as they are made.

## Architecture

- `Attribute`: Low-level, manual control (this class)
- `AttributeArray`: High-level, automatically syncing numpy subclass
- `BlenderObject["attr"]`: Convenience accessor returning AttributeArray

## Parameters

| Name | Type | Description | Default |
|----|----|----|----|
| attribute | `bpy`.[types](https://docs.blender.org/api/current/bpy.types.html#module-bpy.types).[Attribute](https://docs.blender.org/api/current/bpy.types.Attribute.html#bpy.types.Attribute) | The Blender attribute to wrap. | *required* |

## Raises

| Name | Type | Description |
|----|----|----|
|  | [NamedAttributeError](../api/NamedAttributeError.llms.md#databpy.NamedAttributeError) | If the attribute has an unsupported data type. |

## Attributes

| Name | Type | Description |
|----|----|----|
| attribute | `bpy`.[types](https://docs.blender.org/api/current/bpy.types.html#module-bpy.types).[Attribute](https://docs.blender.org/api/current/bpy.types.Attribute.html#bpy.types.Attribute) | The underlying Blender attribute. |
| name | [str](https://docs.python.org/3/builtins/stdtypes.html#str) | Name of the attribute. |
| atype | [AttributeTypes](../api/AttributeTypes.llms.md#databpy.AttributeTypes) | Enum value representing the attribute’s data type. |
| domain | [AttributeDomains](../api/AttributeDomains.llms.md#databpy.AttributeDomains) | Enum value representing the attribute’s domain (POINT, EDGE, FACE, etc.). |
| shape | [tuple](https://docs.python.org/3/builtins/stdtypes.html#tuple) | Full shape including number of elements and component dimensions. |
| dtype | `Type` | NumPy dtype corresponding to the attribute type. |

## Examples

Manual read/write workflow:

``` python
import databpy as db
import numpy as np

obj = db.create_object(np.random.rand(10, 3))
attr = db.Attribute(obj.data.attributes["position"])

# Read once
positions = attr.as_array()
positions[:, 2] += 1.0

# Write once
attr.from_array(positions)
```

Compare with AttributeArray, which writes each change as it is made:

``` python
import databpy as db
import numpy as np

bob = db.create_bob(np.random.rand(10, 3))
bob.position[:, 2] += 1.0  # writes the new z values immediately
```

## See Also

AttributeArray : Automatically syncing numpy subclass store_named_attribute : Create or update attributes named_attribute : Convenience function to read attribute data

## Methods

| Name | Description |
|----|----|
| [as_array](#databpy.Attribute.as_array) | Read the attribute’s values into a new numpy array. |
| [from_array](#databpy.Attribute.from_array) | Write the values of an array to the attribute. |

### as_array

``` python
Attribute.as_array()
```

Read the attribute’s values into a new numpy array.

#### Returns

| Name | Type | Description |
|----|----|----|
|  | [np](https://numpy.org/doc/stable/reference/index.html#module-numpy).[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray) | The values, with the attribute’s `shape` and `dtype`. BYTE_COLOR values are uint8 from 0 to 255. |

### from_array

``` python
Attribute.from_array(array)
```

Write the values of an array to the attribute.

The array can have any shape with the same number of values as the attribute, such as a flat array, and is read in C order. Values are cast to the attribute’s storage dtype.

#### Parameters

| Name | Type | Description | Default |
|----|----|----|----|
| array | [npt](https://numpy.org/doc/stable/reference/typing.html#module-numpy.typing).[ArrayLike](https://numpy.org/doc/stable/reference/typing.html#numpy.typing.ArrayLike) | The values to write, as a numpy array or anything convertible to one. | *required* |

#### Raises

| Name | Type | Description |
|----|----|----|
|  | [AttributeMismatchError](../api/AttributeMismatchError.llms.md#databpy.AttributeMismatchError) | If the number of values doesn’t match the attribute’s `size`, or the values can’t be represented by the attribute’s type. |
