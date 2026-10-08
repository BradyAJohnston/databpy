# AttributeArray

``` python
AttributeArray()
```

A numpy array subclass that automatically syncs changes back to the Blender object.

AttributeArray provides an ergonomic interface for working with Blender attributes using familiar numpy operations. It automatically handles bidirectional syncing: values are retrieved from Blender as a numpy array, operations are applied, and results are immediately stored back to Blender.

This is the high-level interface for attribute manipulation. For low-level control, see the `Attribute` class which provides manual get/set operations without auto-sync.

## Syncing

Changes are written back to Blender by item assignment (`pos[0] = ...`), in-place operators (`pos += 1`, `pos[:, 2] *= 2`), ufuncs with `out=` or `.at`, the `fill`, `sort`, `put` and `partition` methods, and `np.copyto`, `np.place`, `np.putmask` and `np.fill_diagonal`. Writes through `.flat` are not synced.

Other operations (`pos + 1`, `pos.copy()`, `pos[mask]`) return plain or detached arrays that don’t sync. If the object is removed, or a file is loaded, syncing raises a `LinkedObjectError`.

## Performance Characteristics

- Every modification syncs the ENTIRE attribute array to Blender, not just changed values
- This is due to Blender’s foreach_set API requiring the complete array
- For large meshes (10K+ elements), consider batching multiple operations
- Example: `pos[:, 2] += 1.0` writes all position data, not just Z coordinates

## Supported Types

Works with all Blender attribute types: - Float types: FLOAT, FLOAT2, FLOAT4, FLOAT_VECTOR, FLOAT_COLOR, FLOAT4X4, QUATERNION - Integer types: INT (int32), INT8, INT16_2D, INT32_2D - Boolean: BOOLEAN - Color: BYTE_COLOR (uint8) - String: STRING (synced per-element as strings don’t support `foreach_set`)

## Attributes

| Name | Type | Description |
|----|----|----|
| \_link | `_AttributeLink` \| None | Link to the Blender object and attribute, or None for detached copies. |
| \_root | [AttributeArray](../api/AttributeArray.llms.md#databpy.AttributeArray) | Reference to the root array for handling views/slices correctly. |

## Examples

Basic usage:

``` python
import databpy as db
import numpy as np

obj = db.create_object(np.random.rand(10, 3), name="test_bob")
pos = db.AttributeArray(obj, "position")
pos[:, 2] += 1.0  # Automatically syncs to Blender
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
    [[0.25601932 0.79616094 0.3099401 ]
     [0.45610198 0.6883781  0.87819046]
     [0.3053136  0.3288965  0.68523437]
     [0.21568549 0.23069106 0.07536739]
     [0.34745386 0.33714864 0.25851294]
     [0.13989419 0.13942632 0.23319536]
     [0.82846195 0.5376943  0.23613842]
     [0.99722517 0.8365247  0.677525  ]
     [0.6893738  0.26239654 0.35277498]
     [0.02814466 0.34089845 0.05410333]]

``` python
bob.position[:, 2] += 1.0
print('Updated position:')
print(bob.position)
```

    Updated position:
    AttributeArray 'position' from test_bob.001('test_bob.001')(domain: POINT, shape: (10, 3), dtype: float32)
    [[0.25601932 0.79616094 1.3099401 ]
     [0.45610198 0.6883781  1.8781905 ]
     [0.3053136  0.3288965  1.6852343 ]
     [0.21568549 0.23069106 1.0753675 ]
     [0.34745386 0.33714864 1.258513  ]
     [0.13989419 0.13942632 1.2331953 ]
     [0.82846195 0.5376943  1.2361385 ]
     [0.99722517 0.8365247  1.677525  ]
     [0.6893738  0.26239654 1.352775  ]
     [0.02814466 0.34089845 1.0541034 ]]

``` python
# Convert to regular numpy array (no sync)
print('As Array:')
print(np.asarray(bob.position))
```

    As Array:
    [[0.25601932 0.79616094 1.3099401 ]
     [0.45610198 0.6883781  1.8781905 ]
     [0.3053136  0.3288965  1.6852343 ]
     [0.21568549 0.23069106 1.0753675 ]
     [0.34745386 0.33714864 1.258513  ]
     [0.13989419 0.13942632 1.2331953 ]
     [0.82846195 0.5376943  1.2361385 ]
     [0.99722517 0.8365247  1.677525  ]
     [0.6893738  0.26239654 1.352775  ]
     [0.02814466 0.34089845 1.0541034 ]]

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
id_array += 100  # Automatically syncs as int32
```

## See Also

Attribute : Low-level attribute interface without auto-sync store_named_attribute : Function to create/update attributes named_attribute : Function to read attribute data as regular arrays

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
