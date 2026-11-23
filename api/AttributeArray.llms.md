# AttributeArray

``` python
AttributeArray()
```

A numpy array of an attribute’s values that writes changes back to Blender.

Creating the array reads the attribute’s values. Modifying the array in place writes the changed values back to the attribute straight away. For manual control over when values are read and written, use `Attribute`.

## Syncing

Changes are written back to Blender by item assignment (`pos[0] = ...`), in-place operators (`pos += 1`, `pos[:, 2] *= 2`), ufuncs with `out=` or `.at`, the `fill`, `sort`, `put` and `partition` methods, and `np.copyto`, `np.place`, `np.putmask` and `np.fill_diagonal`. Writes through `.flat` are not synced.

Other operations (`pos + 1`, `pos.copy()`, `pos[mask]`) return plain or detached arrays that don’t sync. If the object is removed, or a file is loaded, syncing raises a `LinkedObjectError`.

## Performance Characteristics

- Creating the array copies all of the attribute’s values.
- Each modification writes only the values it changed, directly into the attribute’s memory: `pos[:10, 2] = 1.0` writes 10 values however large the attribute is.
- Where the attribute can’t be written directly, the entire array is written with `store_named_attribute` instead. This applies to STRING attributes, a `SINGLE` value for the whole domain, and an attribute that was removed (which is re-created). If the attribute’s size, type or domain changed since the array was read, this raises a `NamedAttributeError`.

## Supported Types

Every attribute type in `AttributeTypes`, with values in its storage dtype: - Float types (float32): FLOAT, FLOAT2, FLOAT4 (Blender 5.2+), FLOAT_VECTOR, FLOAT_COLOR, FLOAT4X4, QUATERNION - Integer types: INT (int32), INT8, INT16_2D (int16), INT32_2D (int32) - Boolean: BOOLEAN - Color: BYTE_COLOR (uint8) - String: STRING (str), read and written one value at a time

## Attributes

| Name | Type | Description |
|----|----|----|
| \_link | `_AttributeLink` \| None | Link to the Blender object and attribute, or None for detached copies. |
| \_root | [AttributeArray](../api/AttributeArray.llms.md#databpy.AttributeArray) \| None | The array read from Blender that this array is a view of, or None if this is that array (or a detached copy). |

## Examples

Basic usage:

``` python
import databpy as db
import numpy as np

obj = db.create_object(np.random.rand(10, 3), name="test_bob")
pos = db.AttributeArray(obj, "position")
pos[:, 2] += 1.0  # writes the new z values to Blender
```

Using BlenderObject for convenience:

``` python
import databpy as db
import numpy as np

bob = db.create_bob(np.random.rand(10, 3), name="test_bob")
print('Initial position:')
print(bob.position)  # Returns an AttributeArray
```

    Initial position:
    AttributeArray 'position' from test_bob.001('test_bob.001')(domain: POINT, shape: (10, 3), dtype: float32)
    [[0.9817943  0.27205762 0.66738737]
     [0.31025478 0.9886139  0.8159376 ]
     [0.35343176 0.09027418 0.15818886]
     [0.14453782 0.28315654 0.36407712]
     [0.22467192 0.8521142  0.8871629 ]
     [0.49517807 0.80403954 0.8396878 ]
     [0.07162368 0.02323486 0.8734892 ]
     [0.7400954  0.01768341 0.16108832]
     [0.6107718  0.9766339  0.6926967 ]
     [0.76820225 0.8577181  0.05140894]]

``` python
bob.position[:, 2] += 1.0
print('Updated position:')
print(bob.position)
```

    Updated position:
    AttributeArray 'position' from test_bob.001('test_bob.001')(domain: POINT, shape: (10, 3), dtype: float32)
    [[0.9817943  0.27205762 1.6673874 ]
     [0.31025478 0.9886139  1.8159375 ]
     [0.35343176 0.09027418 1.1581888 ]
     [0.14453782 0.28315654 1.3640771 ]
     [0.22467192 0.8521142  1.8871629 ]
     [0.49517807 0.80403954 1.8396878 ]
     [0.07162368 0.02323486 1.8734891 ]
     [0.7400954  0.01768341 1.1610883 ]
     [0.6107718  0.9766339  1.6926967 ]
     [0.76820225 0.8577181  1.0514089 ]]

``` python
# Convert to regular numpy array (no sync)
print('As Array:')
print(np.asarray(bob.position))
```

    As Array:
    [[0.9817943  0.27205762 1.6673874 ]
     [0.31025478 0.9886139  1.8159375 ]
     [0.35343176 0.09027418 1.1581888 ]
     [0.14453782 0.28315654 1.3640771 ]
     [0.22467192 0.8521142  1.8871629 ]
     [0.49517807 0.80403954 1.8396878 ]
     [0.07162368 0.02323486 1.8734891 ]
     [0.7400954  0.01768341 1.1610883 ]
     [0.6107718  0.9766339  1.6926967 ]
     [0.76820225 0.8577181  1.0514089 ]]

Working with integer attributes:

``` python
import databpy as db
import numpy as np

obj = db.create_object(np.random.rand(10, 3))
# Store integer attribute
ids = np.arange(10, dtype=np.int32)
db.store_named_attribute(obj, ids, "id", atype="INT")

# Access as AttributeArray
id_array = db.AttributeArray(obj, "id")
id_array += 100  # stays int32 and writes to Blender
```

## See Also

Attribute : Low-level attribute interface without automatic syncing store_named_attribute : Create or update an attribute named_attribute : Read an attribute’s values as a plain numpy array

## Methods

| Name | Description |
|----|----|
| [fill](#databpy.AttributeArray.fill) | Fill the array with a scalar value and sync to Blender. |
| [partition](#databpy.AttributeArray.partition) | Partition the array in-place and sync to Blender. |
| [put](#databpy.AttributeArray.put) | Set values at the given flat indices and sync to Blender. |
| [sort](#databpy.AttributeArray.sort) | Sort the array in-place and sync to Blender. |

### fill

``` python
AttributeArray.fill(value)
```

Fill the array with a scalar value and sync to Blender.

### partition

``` python
AttributeArray.partition(*args, **kwargs)
```

Partition the array in-place and sync to Blender.

### put

``` python
AttributeArray.put(*args, **kwargs)
```

Set values at the given flat indices and sync to Blender.

### sort

``` python
AttributeArray.sort(*args, **kwargs)
```

Sort the array in-place and sync to Blender.
