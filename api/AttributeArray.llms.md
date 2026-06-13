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
    [[0.8764723  0.5336814  0.19765154]
     [0.19821088 0.2781838  0.6448589 ]
     [0.54490024 0.5927433  0.81545204]
     [0.90268266 0.6126264  0.9556603 ]
     [0.4444654  0.80111444 0.7600288 ]
     [0.5697354  0.04339826 0.37239918]
     [0.4443243  0.5258636  0.9818367 ]
     [0.52361196 0.57028455 0.7884808 ]
     [0.6322411  0.18909138 0.96980715]
     [0.18232642 0.47912636 0.6387195 ]]

``` python
bob.position[:, 2] += 1.0
print('Updated position:')
print(bob.position)
```

    Updated position:
    AttributeArray 'position' from test_bob.001('test_bob.001')(domain: POINT, shape: (10, 3), dtype: float32)
    [[0.8764723  0.5336814  1.1976515 ]
     [0.19821088 0.2781838  1.6448588 ]
     [0.54490024 0.5927433  1.8154521 ]
     [0.90268266 0.6126264  1.9556603 ]
     [0.4444654  0.80111444 1.7600288 ]
     [0.5697354  0.04339826 1.3723992 ]
     [0.4443243  0.5258636  1.9818367 ]
     [0.52361196 0.57028455 1.7884808 ]
     [0.6322411  0.18909138 1.9698071 ]
     [0.18232642 0.47912636 1.6387196 ]]

``` python
# Convert to regular numpy array (no sync)
print('As Array:')
print(np.asarray(bob.position))
```

    As Array:
    [[0.8764723  0.5336814  1.1976515 ]
     [0.19821088 0.2781838  1.6448588 ]
     [0.54490024 0.5927433  1.8154521 ]
     [0.90268266 0.6126264  1.9556603 ]
     [0.4444654  0.80111444 1.7600288 ]
     [0.5697354  0.04339826 1.3723992 ]
     [0.4443243  0.5258636  1.9818367 ]
     [0.52361196 0.57028455 1.7884808 ]
     [0.6322411  0.18909138 1.9698071 ]
     [0.18232642 0.47912636 1.6387196 ]]

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
