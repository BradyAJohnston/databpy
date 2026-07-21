# GeometrySet

``` python
GeometrySet(obj, context=None)
```

Access the evaluated geometry of an object (`bpy.types.GeometrySet`).

Evaluating an object normally only exposes a single geometry data-block, but Geometry Nodes can output multiple components at once - a mesh, a point cloud, curves and instances. This class evaluates the object’s modifiers and provides access to all of the resulting components and their attributes, which is particularly useful for testing node group outputs.

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
|  | [dict](https://docs.python.org/3/library/stdtypes.html#dict)\[`GeometryComponents`, `bpy`.[types](https://docs.blender.org/api/current/bpy.types.html#module-bpy.types).[ID](https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID)\] | A mapping of component names to their data-blocks, containing only the components that are present and contain geometry. Blender can include empty components (e.g. a 0-vertex mesh) in the evaluated geometry, which are excluded here - access the `mesh` etc. properties directly if you need them. |

### list_attributes

``` python
GeometrySet.list_attributes(drop_hidden=False)
```

List the attribute names on each component of the evaluated geometry.

#### Parameters

| Name | Type | Description | Default |
|----|----|----|----|
| drop_hidden | [bool](https://docs.python.org/3/library/functions.html#bool) | Whether to drop hidden attributes (those starting with a dot). Defaults to False. | `False` |

#### Returns

| Name | Type | Description |
|----|----|----|
|  | [dict](https://docs.python.org/3/library/stdtypes.html#dict)\[`GeometryComponents`, [list](https://docs.python.org/3/library/stdtypes.html#list)\[[str](https://docs.python.org/3/library/stdtypes.html#str)\]\] | A mapping of component names to their sorted attribute names. |

### named_attribute

``` python
GeometrySet.named_attribute(name, component=None)
```

Get named attribute data from the evaluated geometry.

#### Parameters

| Name | Type | Description | Default |
|----|----|----|----|
| name | [str](https://docs.python.org/3/library/stdtypes.html#str) | The name of the attribute. | *required* |
| component | `GeometryComponents` | The component to read the attribute from. If None, the components are searched in order (MESH, POINTCLOUD, CURVES, INSTANCES) and the first that has the attribute is used. | `None` |

#### Returns

| Name | Type | Description |
|----|----|----|
|  | [np](https://numpy.org/doc/stable/reference/index.html#module-numpy).[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray) | The attribute data as a numpy array. |

#### Raises

| Name | Type | Description |
|----|----|----|
|  | `NamedAttributeError` | If the attribute does not exist on the given (or any) component. |
