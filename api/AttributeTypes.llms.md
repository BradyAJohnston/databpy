# AttributeTypes

``` python
AttributeTypes()
```

Enumeration of attribute types in Blender.

Each attribute type has a specific data type and dimensionality that corresponds to Blender’s internal CustomData types. The dtype values use explicit NumPy types (e.g., np.float32, np.uint8) that match Blender’s internal storage precision.

## Notes

All float types use np.float32 (not Python’s float or np.float64) as this matches Blender’s internal 32-bit float storage. BYTE_COLOR uses np.uint8 (unsigned) as it corresponds to Blender’s MLoopCol struct which stores color components as unsigned char values (0-255 range).

## Attributes

| Name | Type | Description |
|----|----|----|
| FLOAT | `AttributeType` | Single float value with dimensions (1,). Dtype: np.float32 [More Info](https://docs.blender.org/api/current/bpy.types.FloatAttribute.html#bpy.types.FloatAttribute) |
| FLOAT_VECTOR | `AttributeType` | 3D vector of floats with dimensions (3,). Dtype: np.float32 [More Info](https://docs.blender.org/api/current/bpy.types.FloatVectorAttribute.html#bpy.types.FloatVectorAttribute) |
| FLOAT2 | `AttributeType` | 2D vector of floats with dimensions (2,). Dtype: np.float32 [More Info](https://docs.blender.org/api/current/bpy.types.Float2Attribute.html#bpy.types.Float2Attribute) |
| FLOAT_COLOR | `AttributeType` | RGBA color values as floats with dimensions (4,). Dtype: np.float32 [More Info](https://docs.blender.org/api/current/bpy.types.FloatColorAttributeValue.html#bpy.types.FloatColorAttributeValue) |
| BYTE_COLOR | `AttributeType` | RGBA color values as unsigned 8-bit integers with dimensions (4,). Dtype: np.uint8 [More Info](https://docs.blender.org/api/current/bpy.types.ByteColorAttribute.html#bpy.types.ByteColorAttribute) |
| QUATERNION | `AttributeType` | Quaternion rotation (w, x, y, z) as floats with dimensions (4,). Dtype: np.float32 [More Info](https://docs.blender.org/api/current/bpy.types.QuaternionAttribute.html#bpy.types.QuaternionAttribute) |
| INT | `AttributeType` | Single 32-bit integer value with dimensions (1,). Dtype: np.int32 [More Info](https://docs.blender.org/api/current/bpy.types.IntAttribute.html#bpy.types.IntAttribute) |
| INT8 | `AttributeType` | 8-bit signed integer value with dimensions (1,). Dtype: np.int8 [More Info](https://docs.blender.org/api/current/bpy.types.ByteIntAttributeValue.html#bpy.types.ByteIntAttributeValue) |
| INT32_2D | `AttributeType` | 2D vector of 32-bit integers with dimensions (2,). Dtype: np.int32 [More Info](https://docs.blender.org/api/current/bpy.types.Int2Attribute.html#bpy.types.Int2Attribute) |
| FLOAT4X4 | `AttributeType` | 4x4 transformation matrix of floats with dimensions (4, 4). Dtype: np.float32 [More Info](https://docs.blender.org/api/current/bpy.types.Float4x4Attribute.html#bpy.types.Float4x4Attribute) |
| BOOLEAN | `AttributeType` | Single boolean value with dimensions (1,). Dtype: bool [More Info](https://docs.blender.org/api/current/bpy.types.BoolAttribute.html#bpy.types.BoolAttribute) |
