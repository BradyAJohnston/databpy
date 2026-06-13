# AttributeArray

``` python
AttributeArray()
```

A numpy array subclass that automatically syncs changes back to the Blender object.

AttributeArray provides an ergonomic interface for working with Blender attributes using familiar numpy operations. It automatically handles bidirectional syncing: values are retrieved from Blender as a numpy array, operations are applied, and results are immediately stored back to Blender.

This is the high-level interface for attribute manipulation. For low-level control, see the `Attribute` class which provides manual get/set operations without auto-sync.

## Performance Characteristics

- Every modification syncs the ENTIRE attribute array to Blender, not just changed values
- This is due to Blender’s foreach_set API requiring the complete array
- For large meshes (10K+ elements), consider batching multiple operations
- Example: `pos[:, 2] += 1.0` writes all position data, not just Z coordinates

## Supported Types

Works with all Blender attribute types: - Float types: FLOAT, FLOAT2, FLOAT_VECTOR, FLOAT_COLOR, FLOAT4X4, QUATERNION - Integer types: INT (int32), INT8, INT32_2D - Boolean: BOOLEAN - Color: BYTE_COLOR (uint8)

## Attributes

| Name | Type | Description |
|----|----|----|
| \_blender_object | `bpy`.[types](https://docs.blender.org/api/current/bpy.types.html#module-bpy.types).[Object](https://docs.blender.org/api/current/bpy.types.Object.html#bpy.types.Object) | Reference to the Blender object for syncing changes. |
| \_attribute | `Attribute` | The underlying Attribute instance with type information. |
| \_attr_name | [str](https://docs.python.org/3/library/stdtypes.html#str) | Name of the attribute being wrapped. |
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
    [[0.06377091 0.09359733 0.67478794]
     [0.6988725  0.10491922 0.01401361]
     [0.98690426 0.29901287 0.08069805]
     [0.3708576  0.92906326 0.0813432 ]
     [0.00927019 0.08940405 0.30155545]
     [0.90240526 0.56417406 0.03736033]
     [0.20558009 0.44272622 0.801336  ]
     [0.06851536 0.8951075  0.9979343 ]
     [0.25077438 0.630213   0.5364185 ]
     [0.63291085 0.05065865 0.0564781 ]]

``` python
bob.position[:, 2] += 1.0
print('Updated position:')
print(bob.position)
```

    Updated position:
    AttributeArray 'position' from test_bob.001('test_bob.001')(domain: POINT, shape: (10, 3), dtype: float32)
    [[0.06377091 0.09359733 1.674788  ]
     [0.6988725  0.10491922 1.0140136 ]
     [0.98690426 0.29901287 1.080698  ]
     [0.3708576  0.92906326 1.0813432 ]
     [0.00927019 0.08940405 1.3015554 ]
     [0.90240526 0.56417406 1.0373603 ]
     [0.20558009 0.44272622 1.801336  ]
     [0.06851536 0.8951075  1.9979343 ]
     [0.25077438 0.630213   1.5364184 ]
     [0.63291085 0.05065865 1.0564781 ]]

``` python
# Convert to regular numpy array (no sync)
print('As Array:')
print(np.asarray(bob.position))
```

    As Array:
    [[0.06377091 0.09359733 1.674788  ]
     [0.6988725  0.10491922 1.0140136 ]
     [0.98690426 0.29901287 1.080698  ]
     [0.3708576  0.92906326 1.0813432 ]
     [0.00927019 0.08940405 1.3015554 ]
     [0.90240526 0.56417406 1.0373603 ]
     [0.20558009 0.44272622 1.801336  ]
     [0.06851536 0.8951075  1.9979343 ]
     [0.25077438 0.630213   1.5364184 ]
     [0.63291085 0.05065865 1.0564781 ]]

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
