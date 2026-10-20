# BlenderObject

``` python
BlenderObject(obj=None)
```

A convenience class for working with Blender objects.

Extends BlenderObjectAttribute with methods for creating objects and calculating centroids.

## Attributes

| Name | Description |
|----|----|
| [attributes](#databpy.BlenderObject.attributes) | Get the attributes of the Blender object. |
| [data](#databpy.BlenderObject.data) | Get the data block of the Blender object. |
| [edges](#databpy.BlenderObject.edges) | Get the edges of the Blender mesh object. |
| [name](#databpy.BlenderObject.name) | Get the name of the Blender object. |
| [object](#databpy.BlenderObject.object) | Get the Blender object. |
| [position](#databpy.BlenderObject.position) | Get the positions of the object’s vertices or points. |
| [uuid](#databpy.BlenderObject.uuid) | Get the unique identifier for this object. |
| [vertices](#databpy.BlenderObject.vertices) | Get the vertices of the Blender mesh object. |

## Methods

| Name | Description |
|----|----|
| [centroid](#databpy.BlenderObject.centroid) | Calculate the weighted or unweighted centroid of the object’s positions. |
| [evaluate](#databpy.BlenderObject.evaluate) | Return the evaluated version of the object, with all modifiers applied. |
| [from_curves](#databpy.BlenderObject.from_curves) | Create a BlenderObject from curves data. |
| [from_mesh](#databpy.BlenderObject.from_mesh) | Create a BlenderObject from mesh data. |
| [from_pointcloud](#databpy.BlenderObject.from_pointcloud) | Create a BlenderObject from point cloud data. |
| [list_attributes](#databpy.BlenderObject.list_attributes) | List the names of the object’s attributes. |
| [named_attribute](#databpy.BlenderObject.named_attribute) | Read a named attribute from the object as a numpy array. |
| [new_from_pydata](#databpy.BlenderObject.new_from_pydata) | Replace the geometry of the object’s mesh with vertex, edge and face data. |
| [remove_named_attribute](#databpy.BlenderObject.remove_named_attribute) | Remove a named attribute from the object. |
| [store_named_attribute](#databpy.BlenderObject.store_named_attribute) | Store a named attribute on the Blender object. |

### centroid

``` python
BlenderObject.centroid(weight=None)
```

Calculate the weighted or unweighted centroid of the object’s positions.

#### Parameters

| Name | Type | Description | Default |
|----|----|----|----|
| weight | [str](https://docs.python.org/3/builtins/stdtypes.html#str) \| [np](https://numpy.org/doc/stable/reference/index.html#module-numpy).[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray) \| None | The weights or indices for calculating the centroid. Defaults to None. - str: the name of an attribute, whose values are used as below - float array: a weight for each position - int array: the indices of the positions to include - bool array: a mask of the positions to include - None: all positions, weighted equally | `None` |

#### Returns

| Name | Type | Description |
|----|----|----|
|  | [np](https://numpy.org/doc/stable/reference/index.html#module-numpy).[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray) | The centroid position, with shape (3,). |

#### Raises

| Name | Type | Description |
|----|----|----|
|  | [TypeError](https://docs.python.org/3/builtins/exceptions.html#TypeError) | If `weight` isn’t float, integer or boolean. |
|  | [AttributeNotFoundError](../api/AttributeNotFoundError.llms.md#databpy.AttributeNotFoundError) | If `weight` is the name of an attribute that doesn’t exist. |

### evaluate

``` python
BlenderObject.evaluate()
```

Return the evaluated version of the object, with all modifiers applied.

#### Returns

| Name | Type | Description |
|----|----|----|
|  | [Object](https://docs.blender.org/api/current/bpy.types.Object.html#bpy.types.Object) | The evaluated object from the dependency graph, which isn’t stored in `bpy.data.objects`. |

### from_curves

``` python
BlenderObject.from_curves(
    positions=None,
    curve_sizes=None,
    name='Curves',
    collection=None,
)
```

Create a BlenderObject from curves data.

#### Parameters

| Name | Type | Description | Default |
|----|----|----|----|
| positions | `ndarray` or None | Control point positions with shape (N, 3). Default is None. | `None` |
| curve_sizes | [list](https://docs.python.org/3/builtins/stdtypes.html#list)\[[int](https://docs.python.org/3/builtins/functions.html#int)\] \| [np](https://numpy.org/doc/stable/reference/index.html#module-numpy).[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray) or None | Number of points in each curve. Default is None. | `None` |
| name | [str](https://docs.python.org/3/builtins/stdtypes.html#str) | Name of the created object. Default is “Curves”. | `'Curves'` |
| collection | `bpy`.[types](https://docs.blender.org/api/current/bpy.types.html#module-bpy.types).[Collection](https://docs.blender.org/api/current/bpy.types.Collection.html#bpy.types.Collection) or None | Blender collection to link the object to. Default is None. | `None` |

#### Returns

| Name | Type | Description |
|----|----|----|
|  | [BlenderObject](../api/BlenderObject.llms.md#databpy.BlenderObject) | A wrapped Blender curves object. |

#### Raises

| Name | Type | Description |
|----|----|----|
|  | [ValueError](https://docs.python.org/3/builtins/exceptions.html#ValueError) | If only one of `positions` and `curve_sizes` is given, or their lengths don’t match. |

#### Examples

``` python
import numpy as np
import databpy as db

# Create 2 curves with 3 and 4 points
positions = np.random.random((7, 3))
bob = db.BlenderObject.from_curves(positions, [3, 4], name="MyCurves")
print(len(bob))  # 7
```

### from_mesh

``` python
BlenderObject.from_mesh(
    vertices=None,
    edges=None,
    faces=None,
    name='Mesh',
    collection=None,
)
```

Create a BlenderObject from mesh data.

#### Parameters

| Name | Type | Description | Default |
|----|----|----|----|
| vertices | `ndarray` or None | Array of vertex coordinates with shape (N, 3). Default is None. | `None` |
| edges | `ndarray` or None | Vertex indices of each edge, with shape (M, 2). Default is None. | `None` |
| faces | `ndarray` or None | Vertex indices of each face. Faces with different numbers of vertices can be given as a list of lists. Default is None. | `None` |
| name | [str](https://docs.python.org/3/builtins/stdtypes.html#str) | Name of the created object. Default is “Mesh”. | `'Mesh'` |
| collection | `bpy`.[types](https://docs.blender.org/api/current/bpy.types.html#module-bpy.types).[Collection](https://docs.blender.org/api/current/bpy.types.Collection.html#bpy.types.Collection) or None | Blender collection to link the object to. Default is None. | `None` |

#### Returns

| Name | Type | Description |
|----|----|----|
|  | [BlenderObject](../api/BlenderObject.llms.md#databpy.BlenderObject) | A wrapped Blender mesh object. |

#### Raises

| Name | Type | Description |
|----|----|----|
|  | [ValueError](https://docs.python.org/3/builtins/exceptions.html#ValueError) | If `vertices` doesn’t have the shape (N, 3), an edge doesn’t have exactly 2 vertex indices, or an index is outside of the vertices. |
|  | [TypeError](https://docs.python.org/3/builtins/exceptions.html#TypeError) | If edge or face indices aren’t integers. |

#### Examples

``` python
import numpy as np
import databpy as db

vertices = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]])
bob = db.BlenderObject.from_mesh(vertices=vertices, name="MyMesh")
print(len(bob))  # 4
```

### from_pointcloud

``` python
BlenderObject.from_pointcloud(
    positions=None,
    name='PointCloud',
    collection=None,
)
```

Create a BlenderObject from point cloud data.

#### Parameters

| Name | Type | Description | Default |
|----|----|----|----|
| positions | `ndarray` or None | Point positions with shape (N, 3). Default is None. | `None` |
| name | [str](https://docs.python.org/3/builtins/stdtypes.html#str) | Name of the created object. Default is “PointCloud”. | `'PointCloud'` |
| collection | `bpy`.[types](https://docs.blender.org/api/current/bpy.types.html#module-bpy.types).[Collection](https://docs.blender.org/api/current/bpy.types.Collection.html#bpy.types.Collection) or None | Blender collection to link the object to. Default is None. | `None` |

#### Returns

| Name | Type | Description |
|----|----|----|
|  | [BlenderObject](../api/BlenderObject.llms.md#databpy.BlenderObject) | A wrapped Blender point cloud object. |

#### Examples

``` python
import numpy as np
import databpy as db

# Create point cloud with 100 random points
positions = np.random.random((100, 3))
bob = db.BlenderObject.from_pointcloud(positions, name="MyPointCloud")
print(len(bob))  # 100
```

### list_attributes

``` python
BlenderObject.list_attributes(evaluate=False, drop_hidden=False)
```

List the names of the object’s attributes.

#### Parameters

| Name | Type | Description | Default |
|----|----|----|----|
| evaluate | [bool](https://docs.python.org/3/builtins/functions.html#bool) | Whether to first evaluate the modifiers on the object before listing the available attributes. Defaults to False. | `False` |
| drop_hidden | [bool](https://docs.python.org/3/builtins/functions.html#bool) | Whether to drop hidden attributes (those starting with a dot). Defaults to False. | `False` |

#### Returns

| Name | Type | Description |
|----|----|----|
|  | [list](https://docs.python.org/3/builtins/stdtypes.html#list)\[[str](https://docs.python.org/3/builtins/stdtypes.html#str)\] | The attribute names. |

### named_attribute

``` python
BlenderObject.named_attribute(name, evaluate=False)
```

Read a named attribute from the object as a numpy array.

#### Parameters

| Name | Type | Description | Default |
|----|----|----|----|
| name | [str](https://docs.python.org/3/builtins/stdtypes.html#str) | Name of the attribute to get. | *required* |
| evaluate | [bool](https://docs.python.org/3/builtins/functions.html#bool) | Whether to evaluate the object’s modifiers before reading the attribute. Defaults to False. | `False` |

#### Returns

| Name | Type | Description |
|----|----|----|
|  | [np](https://numpy.org/doc/stable/reference/index.html#module-numpy).[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray) | A copy of the attribute’s values, which doesn’t sync back to Blender. |

#### Raises

| Name | Type | Description |
|----|----|----|
|  | [AttributeNotFoundError](../api/AttributeNotFoundError.llms.md#databpy.AttributeNotFoundError) | If the attribute doesn’t exist. |

### new_from_pydata

``` python
BlenderObject.new_from_pydata(vertices=None, edges=None, faces=None)
```

Replace the geometry of the object’s mesh with vertex, edge and face data.

#### Parameters

| Name | Type | Description | Default |
|----|----|----|----|
| vertices | [np](https://numpy.org/doc/stable/reference/index.html#module-numpy).[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray) or None | Vertex coordinates with shape (N, 3). | `None` |
| edges | [np](https://numpy.org/doc/stable/reference/index.html#module-numpy).[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray) or None | Vertex indices of each edge, with shape (M, 2). | `None` |
| faces | [np](https://numpy.org/doc/stable/reference/index.html#module-numpy).[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray) or None | Vertex indices of each face. Faces with different numbers of vertices can be given as a list of lists. | `None` |

#### Returns

| Name | Type | Description |
|----|----|----|
|  | [Object](https://docs.blender.org/api/current/bpy.types.Object.html#bpy.types.Object) | The object, with its mesh’s geometry replaced. |

#### Raises

| Name | Type | Description |
|----|----|----|
|  | [TypeError](https://docs.python.org/3/builtins/exceptions.html#TypeError) | If the object is not a mesh, or edge or face indices aren’t integers. |
|  | [ValueError](https://docs.python.org/3/builtins/exceptions.html#ValueError) | If `vertices` doesn’t have the shape (N, 3), an edge doesn’t have exactly 2 vertex indices, or an index is outside of the vertices. |

### remove_named_attribute

``` python
BlenderObject.remove_named_attribute(name)
```

Remove a named attribute from the object.

#### Parameters

| Name | Type | Description | Default |
|----|----|----|----|
| name | [str](https://docs.python.org/3/builtins/stdtypes.html#str) | The name of the attribute to remove. | *required* |

#### Raises

| Name | Type | Description |
|----|----|----|
|  | [AttributeNotFoundError](../api/AttributeNotFoundError.llms.md#databpy.AttributeNotFoundError) | If the attribute doesn’t exist. |
|  | [NamedAttributeError](../api/NamedAttributeError.llms.md#databpy.NamedAttributeError) | If the attribute is required by Blender (e.g. `position`) and can’t be removed. |

### store_named_attribute

``` python
BlenderObject.store_named_attribute(data, name, atype=None, domain=None)
```

Store a named attribute on the Blender object.

#### Parameters

| Name | Type | Description | Default |
|----|----|----|----|
| data | [np](https://numpy.org/doc/stable/reference/index.html#module-numpy).[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray) | The data to be stored as an attribute. | *required* |
| name | [str](https://docs.python.org/3/builtins/stdtypes.html#str) | The name for the attribute. An existing attribute with this name is overwritten, keeping its type and domain. | *required* |
| atype | [str](https://docs.python.org/3/builtins/stdtypes.html#str) or [AttributeTypes](../api/AttributeTypes.llms.md#databpy.AttributeTypes) or None | The attribute type to store the data as. Either string or selection from the AttributeTypes enum. None uses the type of an existing attribute, otherwise infers the attribute type from the input array. | `None` |
| domain | [str](https://docs.python.org/3/builtins/stdtypes.html#str) or [AttributeDomains](../api/AttributeDomains.llms.md#databpy.AttributeDomains) or None | The domain to store the attribute on. None uses the domain of an existing attribute, otherwise AttributeDomains.POINT. | `None` |

#### Returns

| Name | Type | Description |
|----|----|----|
|  | `bpy`.[types](https://docs.blender.org/api/current/bpy.types.html#module-bpy.types).[Attribute](https://docs.blender.org/api/current/bpy.types.Attribute.html#bpy.types.Attribute) | The added or modified attribute. |

#### Raises

| Name | Type | Description |
|----|----|----|
|  | [TypeError](https://docs.python.org/3/builtins/exceptions.html#TypeError) | If the object’s data is not a Mesh, Curves or PointCloud. |
|  | [ValueError](https://docs.python.org/3/builtins/exceptions.html#ValueError) | If `atype` or `domain` isn’t a valid name, no type can be inferred, or `atype` is FLOAT4 before Blender 5.2. |
|  | [NamedAttributeError](../api/NamedAttributeError.llms.md#databpy.NamedAttributeError) | If the data length doesn’t match the domain size, or `atype` or `domain` conflict with an existing attribute. |
|  | [AttributeMismatchError](../api/AttributeMismatchError.llms.md#databpy.AttributeMismatchError) | If the values can’t be represented by the attribute’s type. |
