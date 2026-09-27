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
    [[0.85493296 0.26510254 0.53331715]
     [0.30681923 0.74060124 0.7171653 ]
     [0.30642015 0.7410065  0.91750836]
     [0.29925293 0.1590265  0.3935563 ]
     [0.08549345 0.24925674 0.93933177]
     [0.66976726 0.7500259  0.75108945]
     [0.9346324  0.2545115  0.04834617]
     [0.8814895  0.4373572  0.9538264 ]
     [0.12332802 0.06911905 0.7156254 ]
     [0.49863532 0.10793674 0.15716378]]

``` python
bob.position[:, 2] += 1.0
print('Updated position:')
print(bob.position)
```

    Updated position:
    AttributeArray 'position' from test_bob.001('test_bob.001')(domain: POINT, shape: (10, 3), dtype: float32)
    [[0.85493296 0.26510254 1.5333171 ]
     [0.30681923 0.74060124 1.7171652 ]
     [0.30642015 0.7410065  1.9175084 ]
     [0.29925293 0.1590265  1.3935564 ]
     [0.08549345 0.24925674 1.9393318 ]
     [0.66976726 0.7500259  1.7510895 ]
     [0.9346324  0.2545115  1.0483462 ]
     [0.8814895  0.4373572  1.9538264 ]
     [0.12332802 0.06911905 1.7156254 ]
     [0.49863532 0.10793674 1.1571637 ]]

``` python
# Convert to regular numpy array (no sync)
print('As Array:')
print(np.asarray(bob.position))
```

    As Array:
    [[0.85493296 0.26510254 1.5333171 ]
     [0.30681923 0.74060124 1.7171652 ]
     [0.30642015 0.7410065  1.9175084 ]
     [0.29925293 0.1590265  1.3935564 ]
     [0.08549345 0.24925674 1.9393318 ]
     [0.66976726 0.7500259  1.7510895 ]
     [0.9346324  0.2545115  1.0483462 ]
     [0.8814895  0.4373572  1.9538264 ]
     [0.12332802 0.06911905 1.7156254 ]
     [0.49863532 0.10793674 1.1571637 ]]

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
