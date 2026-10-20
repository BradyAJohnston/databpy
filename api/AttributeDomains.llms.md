# AttributeDomains

``` python
AttributeDomains()
```

Enumeration of attribute domains in Blender.

Every attribute is stored on a domain, and has one value per element of that domain. An attribute can only be stored on a domain the geometry has.

[More Info](https://docs.blender.org/api/current/bpy_types_enum_items/attribute_domain_items.html#rna-enum-attribute-domain-items)

## Attributes

| Name | Type | Description |
|----|----|----|
| POINT | [str](https://docs.python.org/3/builtins/stdtypes.html#str) | The point domain of geometry data which includes vertices, point cloud and control points of curves. |
| EDGE | [str](https://docs.python.org/3/builtins/stdtypes.html#str) | The edges of meshes, defined as pairs of vertices. |
| FACE | [str](https://docs.python.org/3/builtins/stdtypes.html#str) | The face domain of meshes, defined as groups of edges. |
| CORNER | [str](https://docs.python.org/3/builtins/stdtypes.html#str) | The face corners of meshes, one for each vertex of each face. |
| CURVE | [str](https://docs.python.org/3/builtins/stdtypes.html#str) | The Spline domain, which includes the individual splines that each contain at least one control point. |
| INSTANCE | [str](https://docs.python.org/3/builtins/stdtypes.html#str) | The Instance domain, which can include sets of other geometry to be treated as a single group. |
| LAYER | [str](https://docs.python.org/3/builtins/stdtypes.html#str) | The domain of single Grease Pencil layers. |
