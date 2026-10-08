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
    [[4.72409964e-01 5.69770277e-01 7.84869432e-01]
     [5.55031538e-01 5.18389761e-01 2.95582473e-01]
     [4.69306290e-01 3.14400107e-01 6.20933712e-01]
     [6.01915181e-01 6.84577465e-01 1.13311864e-01]
     [4.86474127e-01 6.40753686e-01 9.14400399e-01]
     [9.96618390e-01 4.74473238e-01 3.90265465e-01]
     [4.14494723e-01 7.47113407e-01 1.70601308e-01]
     [7.41542317e-05 5.98161757e-01 8.46979320e-01]
     [4.31788802e-01 4.21684891e-01 9.50431943e-01]
     [6.00452840e-01 2.27974594e-01 8.40415955e-01]]

``` python
bob.position[:, 2] += 1.0
print('Updated position:')
print(bob.position)
```

    Updated position:
    AttributeArray 'position' from test_bob.001('test_bob.001')(domain: POINT, shape: (10, 3), dtype: float32)
    [[4.7240996e-01 5.6977028e-01 1.7848694e+00]
     [5.5503154e-01 5.1838976e-01 1.2955825e+00]
     [4.6930629e-01 3.1440011e-01 1.6209338e+00]
     [6.0191518e-01 6.8457747e-01 1.1133119e+00]
     [4.8647413e-01 6.4075369e-01 1.9144003e+00]
     [9.9661839e-01 4.7447324e-01 1.3902655e+00]
     [4.1449472e-01 7.4711341e-01 1.1706014e+00]
     [7.4154232e-05 5.9816176e-01 1.8469794e+00]
     [4.3178880e-01 4.2168489e-01 1.9504319e+00]
     [6.0045284e-01 2.2797459e-01 1.8404160e+00]]

``` python
# Convert to regular numpy array (no sync)
print('As Array:')
print(np.asarray(bob.position))
```

    As Array:
    [[4.7240996e-01 5.6977028e-01 1.7848694e+00]
     [5.5503154e-01 5.1838976e-01 1.2955825e+00]
     [4.6930629e-01 3.1440011e-01 1.6209338e+00]
     [6.0191518e-01 6.8457747e-01 1.1133119e+00]
     [4.8647413e-01 6.4075369e-01 1.9144003e+00]
     [9.9661839e-01 4.7447324e-01 1.3902655e+00]
     [4.1449472e-01 7.4711341e-01 1.1706014e+00]
     [7.4154232e-05 5.9816176e-01 1.8469794e+00]
     [4.3178880e-01 4.2168489e-01 1.9504319e+00]
     [6.0045284e-01 2.2797459e-01 1.8404160e+00]]

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
