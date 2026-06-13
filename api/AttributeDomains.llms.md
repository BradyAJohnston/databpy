# AttributeDomains

``` python
AttributeDomains()
```

Enumeration of attribute domains in Blender. You can store an attribute onto one of these domains if there is corressponding geometry. All data is on a domain on geometry.

[More Info](https://docs.blender.org/api/current/bpy_types_enum_items/attribute_domain_items.html#rna-enum-attribute-domain-items)

## Attributes

| Name | Type | Description |
|----|----|----|
| POINT | [str](https://docs.python.org/3/library/stdtypes.html#str) | The point domain of geometry data which includes vertices, point cloud and control points of curves. |
| EDGE | [str](https://docs.python.org/3/library/stdtypes.html#str) | The edges of meshes, defined as pairs of vertices. |
| FACE | [str](https://docs.python.org/3/library/stdtypes.html#str) | The face domain of meshes, defined as groups of edges. |
| CORNER | [str](https://docs.python.org/3/library/stdtypes.html#str) | The face domain of meshes, defined as pairs of edges that share a vertex. |
| CURVE | [str](https://docs.python.org/3/library/stdtypes.html#str) | The Spline domain, which includes the individual splines that each contain at least one control point. |
| INSTANCE | [str](https://docs.python.org/3/library/stdtypes.html#str) | The Instance domain, which can include sets of other geometry to be treated as a single group. |
| LAYER | [str](https://docs.python.org/3/library/stdtypes.html#str) | The domain of single Grease Pencil layers. |
