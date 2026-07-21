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

Works with all Blender attribute types: - Float types: FLOAT, FLOAT2, FLOAT4, FLOAT_VECTOR, FLOAT_COLOR, FLOAT4X4, QUATERNION - Integer types: INT (int32), INT8, INT16_2D, INT32_2D - Boolean: BOOLEAN - Color: BYTE_COLOR (uint8) - String: STRING (synced per-element as strings don’t support `foreach_set`)

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
    [[0.29318    0.99019444 0.1346354 ]
     [0.19220234 0.89007443 0.03713289]
     [0.12052336 0.48876375 0.80600643]
     [0.0521957  0.299532   0.41330963]
     [0.21266584 0.76043934 0.7533772 ]
     [0.07490475 0.9887004  0.48241824]
     [0.17699857 0.87481    0.38601896]
     [0.39374748 0.40176523 0.44612154]
     [0.36357155 0.6508813  0.7646437 ]
     [0.8914737  0.47748503 0.2784503 ]]

``` python
bob.position[:, 2] += 1.0
print('Updated position:')
print(bob.position)
```

    Updated position:
    AttributeArray 'position' from test_bob.001('test_bob.001')(domain: POINT, shape: (10, 3), dtype: float32)
    [[0.29318    0.99019444 1.1346354 ]
     [0.19220234 0.89007443 1.0371329 ]
     [0.12052336 0.48876375 1.8060064 ]
     [0.0521957  0.299532   1.4133096 ]
     [0.21266584 0.76043934 1.7533772 ]
     [0.07490475 0.9887004  1.4824183 ]
     [0.17699857 0.87481    1.386019  ]
     [0.39374748 0.40176523 1.4461216 ]
     [0.36357155 0.6508813  1.7646437 ]
     [0.8914737  0.47748503 1.2784503 ]]

``` python
# Convert to regular numpy array (no sync)
print('As Array:')
print(np.asarray(bob.position))
```

    As Array:
    [[0.29318    0.99019444 1.1346354 ]
     [0.19220234 0.89007443 1.0371329 ]
     [0.12052336 0.48876375 1.8060064 ]
     [0.0521957  0.299532   1.4133096 ]
     [0.21266584 0.76043934 1.7533772 ]
     [0.07490475 0.9887004  1.4824183 ]
     [0.17699857 0.87481    1.386019  ]
     [0.39374748 0.40176523 1.4461216 ]
     [0.36357155 0.6508813  1.7646437 ]
     [0.8914737  0.47748503 1.2784503 ]]

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
