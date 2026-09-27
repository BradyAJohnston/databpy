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
| \_attr_name | [str](https://docs.python.org/3/builtins/stdtypes.html#str) | Name of the attribute being wrapped. |
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
    [[0.08519451 0.12593558 0.73475355]
     [0.9307156  0.9718119  0.07536577]
     [0.9999933  0.9402475  0.04354297]
     [0.5477702  0.6138743  0.09345043]
     [0.79537034 0.9728326  0.459035  ]
     [0.00572387 0.13590908 0.5142813 ]
     [0.52112395 0.0110083  0.82412577]
     [0.9702636  0.04447497 0.061113  ]
     [0.94849247 0.8218436  0.3123446 ]
     [0.10509195 0.27289036 0.5416162 ]]

``` python
bob.position[:, 2] += 1.0
print('Updated position:')
print(bob.position)
```

    Updated position:
    AttributeArray 'position' from test_bob.001('test_bob.001')(domain: POINT, shape: (10, 3), dtype: float32)
    [[0.08519451 0.12593558 1.7347536 ]
     [0.9307156  0.9718119  1.0753658 ]
     [0.9999933  0.9402475  1.043543  ]
     [0.5477702  0.6138743  1.0934504 ]
     [0.79537034 0.9728326  1.459035  ]
     [0.00572387 0.13590908 1.5142813 ]
     [0.52112395 0.0110083  1.8241258 ]
     [0.9702636  0.04447497 1.061113  ]
     [0.94849247 0.8218436  1.3123446 ]
     [0.10509195 0.27289036 1.5416162 ]]

``` python
# Convert to regular numpy array (no sync)
print('As Array:')
print(np.asarray(bob.position))
```

    As Array:
    [[0.08519451 0.12593558 1.7347536 ]
     [0.9307156  0.9718119  1.0753658 ]
     [0.9999933  0.9402475  1.043543  ]
     [0.5477702  0.6138743  1.0934504 ]
     [0.79537034 0.9728326  1.459035  ]
     [0.00572387 0.13590908 1.5142813 ]
     [0.52112395 0.0110083  1.8241258 ]
     [0.9702636  0.04447497 1.061113  ]
     [0.94849247 0.8218436  1.3123446 ]
     [0.10509195 0.27289036 1.5416162 ]]

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
