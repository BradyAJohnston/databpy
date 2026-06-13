# BlenderObjectAttribute

``` python
BlenderObjectAttribute(obj=None)
```

Minimal base class for Blender objects with attribute access.

This class provides core functionality for storing and accessing named attributes on Blender objects.

It is intended for use with Mesh, PointCloud and Curves type objects for easier and “numpy-like” attribute access.

It can be inherited by other classes for easier attribute management on objects.

## Attributes

| Name | Type | Description |
|----|----|----|
| position | [AttributeArray](../api/AttributeArray.llms.md#databpy.AttributeArray) | Position attribute of the object’s vertices/points. |
| data | `bpy`.[types](https://docs.blender.org/api/current/bpy.types.html#module-bpy.types).[Mesh](https://docs.blender.org/api/current/bpy.types.Mesh.html#bpy.types.Mesh) \| `bpy`.[types](https://docs.blender.org/api/current/bpy.types.html#module-bpy.types).[Curves](https://docs.blender.org/api/current/bpy.types.Curves.html#bpy.types.Curves) \| `bpy`.[types](https://docs.blender.org/api/current/bpy.types.html#module-bpy.types).[PointCloud](https://docs.blender.org/api/current/bpy.types.PointCloud.html#bpy.types.PointCloud) | The data block associated with this object. |
| attributes |  | Get the attributes collection of the Blender object. |

## Methods

| Name | Description |
|----|----|
| [evaluate](#databpy.BlenderObjectAttribute.evaluate) | Return a version of the object with all modifiers applied. |
| [list_attributes](#databpy.BlenderObjectAttribute.list_attributes) | Returns a list of attribute names for the object. |
| [named_attribute](#databpy.BlenderObjectAttribute.named_attribute) | Retrieve a named attribute from the object. |
| [remove_named_attribute](#databpy.BlenderObjectAttribute.remove_named_attribute) | Remove a named attribute from the object. |
| [store_named_attribute](#databpy.BlenderObjectAttribute.store_named_attribute) | Store a named attribute on the Blender object. |

### evaluate

``` python
BlenderObjectAttribute.evaluate()
```

Return a version of the object with all modifiers applied.

#### Returns

| Name | Type | Description |
|----|----|----|
|  | [Object](https://docs.blender.org/api/current/bpy.types.Object.html#bpy.types.Object) | A new Object that isn’t yet registered with the database |

### list_attributes

``` python
BlenderObjectAttribute.list_attributes(evaluate=False, drop_hidden=False)
```

Returns a list of attribute names for the object.

#### Parameters

| Name | Type | Description | Default |
|----|----|----|----|
| evaluate | [bool](https://docs.python.org/3/library/functions.html#bool) | Whether to first evaluate the modifiers on the object before listing the available attributes. | `False` |
| drop_hidden | [bool](https://docs.python.org/3/library/functions.html#bool) | Whether to drop hidden attributes (those starting with a dot). Defaults to False. | `False` |

#### Returns

| Name | Type | Description |
|----|----|----|
|  | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[str](https://docs.python.org/3/library/stdtypes.html#str)\] \| None | A list of attribute names if the molecule object exists, None otherwise. |

### named_attribute

``` python
BlenderObjectAttribute.named_attribute(name, evaluate=False)
```

Retrieve a named attribute from the object.

Optionally, evaluate the object before reading the named attribute

#### Parameters

| Name | Type | Description | Default |
|----|----|----|----|
| name | [str](https://docs.python.org/3/library/stdtypes.html#str) | Name of the attribute to get. | *required* |
| evaluate | [bool](https://docs.python.org/3/library/functions.html#bool) | Whether to evaluate the object before reading the attribute (default is False). | `False` |

#### Returns

| Name | Type | Description |
|----|----|----|
|  | [np](https://numpy.org/doc/stable/reference/index.html#module-numpy).[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray) | The attribute read from the mesh as a numpy array. |

### remove_named_attribute

``` python
BlenderObjectAttribute.remove_named_attribute(name)
```

Remove a named attribute from the object.

#### Parameters

| Name | Type | Description | Default |
|----|----|----|----|
| name | [str](https://docs.python.org/3/library/stdtypes.html#str) | The name of the attribute to remove. | *required* |

### store_named_attribute

``` python
BlenderObjectAttribute.store_named_attribute(
    data,
    name,
    atype=None,
    domain=AttributeDomains.POINT,
)
```

Store a named attribute on the Blender object.

#### Parameters

| Name | Type | Description | Default |
|----|----|----|----|
| data | [np](https://numpy.org/doc/stable/reference/index.html#module-numpy).[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray) | The data to be stored as an attribute. | *required* |
| name | [str](https://docs.python.org/3/library/stdtypes.html#str) | The name for the attribute. Will overwrite an already existing attribute. | *required* |
| atype | [str](https://docs.python.org/3/library/stdtypes.html#str) or `AttributeType` or None | The attribute type to store the data as. Either string or selection from the AttributeTypes enum. None will attempt to infer the attribute type from the input array. | `None` |
| domain | [str](https://docs.python.org/3/library/stdtypes.html#str) or `AttributeDomain` | The domain to store the attribute on. Defaults to Domains.POINT. | `AttributeDomains.POINT` |

#### Returns

| Name | Type   | Description |
|------|--------|-------------|
|      | `self` |             |
