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
    [[0.8159451  0.22164091 0.6054767 ]
     [0.11721323 0.5914382  0.3725798 ]
     [0.47905883 0.6434982  0.13499004]
     [0.32528788 0.4538986  0.16545187]
     [0.05203167 0.78007096 0.49389982]
     [0.81381613 0.3698646  0.01598053]
     [0.9621401  0.828609   0.8728848 ]
     [0.68874955 0.5318719  0.20737469]
     [0.8270615  0.25852    0.6461827 ]
     [0.7300434  0.74786454 0.0328449 ]]

``` python
bob.position[:, 2] += 1.0
print('Updated position:')
print(bob.position)
```

    Updated position:
    AttributeArray 'position' from test_bob.001('test_bob.001')(domain: POINT, shape: (10, 3), dtype: float32)
    [[0.8159451  0.22164091 1.6054766 ]
     [0.11721323 0.5914382  1.3725798 ]
     [0.47905883 0.6434982  1.13499   ]
     [0.32528788 0.4538986  1.1654519 ]
     [0.05203167 0.78007096 1.4938998 ]
     [0.81381613 0.3698646  1.0159805 ]
     [0.9621401  0.828609   1.8728848 ]
     [0.68874955 0.5318719  1.2073747 ]
     [0.8270615  0.25852    1.6461828 ]
     [0.7300434  0.74786454 1.0328449 ]]

``` python
# Convert to regular numpy array (no sync)
print('As Array:')
print(np.asarray(bob.position))
```

    As Array:
    [[0.8159451  0.22164091 1.6054766 ]
     [0.11721323 0.5914382  1.3725798 ]
     [0.47905883 0.6434982  1.13499   ]
     [0.32528788 0.4538986  1.1654519 ]
     [0.05203167 0.78007096 1.4938998 ]
     [0.81381613 0.3698646  1.0159805 ]
     [0.9621401  0.828609   1.8728848 ]
     [0.68874955 0.5318719  1.2073747 ]
     [0.8270615  0.25852    1.6461828 ]
     [0.7300434  0.74786454 1.0328449 ]]

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
