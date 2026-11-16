# GeometrySet

``` python
GeometrySet(obj, context=None)
```

Access the evaluated geometry of an object (`bpy.types.GeometrySet`).

Evaluating an object normally only exposes a single geometry data-block, but Geometry Nodes can output multiple components at once: a mesh, a point cloud, curves, grease pencil and instances. This class evaluates the object’s modifiers and gives access to all of the resulting components and their attributes, for example to test the output of a node group.

## Parameters

| Name | Type | Description | Default |
|----|----|----|----|
| obj | `bpy`.[types](https://docs.blender.org/api/current/bpy.types.html#module-bpy.types).[Object](https://docs.blender.org/api/current/bpy.types.Object.html#bpy.types.Object) | The Blender object to evaluate. | *required* |
| context | `bpy`.[types](https://docs.blender.org/api/current/bpy.types.html#module-bpy.types).[Context](https://docs.blender.org/api/current/bpy.types.Context.html#bpy.types.Context) | The context used to get the evaluated depsgraph. Defaults to `bpy.context`. | `None` |

## Attributes

| Name | Type | Description |
|----|----|----|
| object | `bpy`.[types](https://docs.blender.org/api/current/bpy.types.html#module-bpy.types).[Object](https://docs.blender.org/api/current/bpy.types.Object.html#bpy.types.Object) | The original (unevaluated) object. |
| evaluated_object | `bpy`.[types](https://docs.blender.org/api/current/bpy.types.html#module-bpy.types).[Object](https://docs.blender.org/api/current/bpy.types.Object.html#bpy.types.Object) | The evaluated object from the depsgraph. |
| geometry | `bpy`.[types](https://docs.blender.org/api/current/bpy.types.html#module-bpy.types).[GeometrySet](https://docs.blender.org/api/current/bpy.types.GeometrySet.html#bpy.types.GeometrySet) | The underlying evaluated geometry. |

## Notes

The evaluated geometry is a snapshot from when the `GeometrySet` was created, and doesn’t change when the object is changed afterwards. Its components, such as `mesh` and `instances`, are owned by the `GeometrySet` and freed with it, so keep a reference to it while using them. `db.GeometrySet(obj).mesh.vertices` raises a `ReferenceError`, as the `GeometrySet` is freed before the mesh is used.

## Examples

``` python
import bpy
import databpy as db

geom = db.GeometrySet(bpy.data.objects["Cube"])
geom.named_attribute("position")
```

    array([[ 1.,  1.,  1.],
           [ 1.,  1., -1.],
           [ 1., -1.,  1.],
           [ 1., -1., -1.],
           [-1.,  1.,  1.],
           [-1.,  1., -1.],
           [-1., -1.,  1.],
           [-1., -1., -1.]], dtype=float32)

``` python
geom.list_attributes()
```

    {'MESH': ['.corner_edge',
      '.corner_vert',
      '.edge_verts',
      '.select_edge',
      '.select_poly',
      '.select_vert',
      '.uv_select_edge',
      '.uv_select_face',
      '.uv_select_vert',
      'UVMap',
      'position',
      'sharp_face']}

## See Also

named_attribute : Read attribute data from an object’s data-block evaluate_object : Evaluate an object to a single data-block

## Methods

| Name | Description |
|----|----|
| [components](#databpy.GeometrySet.components) | Get the attribute-holding components present in the evaluated geometry. |
| [list_attributes](#databpy.GeometrySet.list_attributes) | List the attribute names on each component of the evaluated geometry. |
| [named_attribute](#databpy.GeometrySet.named_attribute) | Get named attribute data from the evaluated geometry. |

### components

``` python
GeometrySet.components()
```

Get the attribute-holding components present in the evaluated geometry.

#### Returns

| Name | Type | Description |
|----|----|----|
|  | [dict](https://docs.python.org/3/builtins/stdtypes.html#dict)\[`GeometryComponents`, `AttributeDataBlock`\] | A mapping of component names to their data-blocks, containing only the components that are present and contain geometry. Blender can include empty components (e.g. a 0-vertex mesh) in the evaluated geometry, which are excluded here; the `mesh`, `pointcloud`, `curves` and `instances` properties still return them. |

### list_attributes

``` python
GeometrySet.list_attributes(drop_hidden=False)
```

List the attribute names on each component of the evaluated geometry.

#### Parameters

| Name | Type | Description | Default |
|----|----|----|----|
| drop_hidden | [bool](https://docs.python.org/3/builtins/functions.html#bool) | Whether to drop hidden attributes (those starting with a dot). Defaults to False. | `False` |

#### Returns

| Name | Type | Description |
|----|----|----|
|  | [dict](https://docs.python.org/3/builtins/stdtypes.html#dict)\[`GeometryComponents`, [list](https://docs.python.org/3/builtins/stdtypes.html#list)\[[str](https://docs.python.org/3/builtins/stdtypes.html#str)\]\] | A mapping of component names to their sorted attribute names. |

### named_attribute

``` python
GeometrySet.named_attribute(name, component=None, *, atype=None)
```

Get named attribute data from the evaluated geometry.

#### Parameters

| Name | Type | Description | Default |
|----|----|----|----|
| name | [str](https://docs.python.org/3/builtins/stdtypes.html#str) | The name of the attribute. | *required* |
| component | `GeometryComponents` | The component to read the attribute from. If None, the components are searched in order (MESH, POINTCLOUD, CURVES, GREASE_PENCIL, INSTANCES) and the first that has the attribute is used. | `None` |
| atype | [type](https://docs.python.org/3/builtins/functions.html#type)\[[AttributeArray](../api/AttributeArray.llms.md#databpy.AttributeArray)\] or None | The typed array class the attribute is expected to be, such as `vec3`. The values are returned as that class, which type checkers also see. | `None` |

#### Returns

| Name | Type | Description |
|----|----|----|
|  | [np](https://numpy.org/doc/stable/reference/index.html#module-numpy).[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray) | The attribute data as a numpy array, or an array of `atype` if given. |

#### Raises

| Name | Type | Description |
|----|----|----|
|  | [AttributeNotFoundError](../api/AttributeNotFoundError.llms.md#databpy.AttributeNotFoundError) | If the attribute does not exist on the given (or any) component. |
|  | [NamedAttributeError](../api/NamedAttributeError.llms.md#databpy.NamedAttributeError) | If the given component isn’t present, or the attribute found isn’t `atype`. Without a component, only the first attribute found is checked. |
