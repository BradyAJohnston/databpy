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
| attributes |  | The attributes collection of the object’s data-block. |

## Methods

| Name | Description |
|----|----|
| [evaluate](#databpy.BlenderObjectAttribute.evaluate) | Return the evaluated version of the object, with all modifiers applied. |
| [list_attributes](#databpy.BlenderObjectAttribute.list_attributes) | List the names of the object’s attributes. |
| [named_attribute](#databpy.BlenderObjectAttribute.named_attribute) | Read a named attribute from the object as a numpy array. |
| [remove_named_attribute](#databpy.BlenderObjectAttribute.remove_named_attribute) | Remove a named attribute from the object. |
| [store_named_attribute](#databpy.BlenderObjectAttribute.store_named_attribute) | Store a named attribute on the Blender object. |

### evaluate

``` python
BlenderObjectAttribute.evaluate()
```

Return the evaluated version of the object, with all modifiers applied.

#### Returns

| Name | Type | Description |
|----|----|----|
|  | [Object](https://docs.blender.org/api/current/bpy.types.Object.html#bpy.types.Object) | The evaluated object from the dependency graph, which isn’t stored in `bpy.data.objects`. |

### list_attributes

``` python
BlenderObjectAttribute.list_attributes(evaluate=False, drop_hidden=False)
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
BlenderObjectAttribute.named_attribute(name, evaluate=False)
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

### remove_named_attribute

``` python
BlenderObjectAttribute.remove_named_attribute(name)
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
BlenderObjectAttribute.store_named_attribute(
    data,
    name,
    atype=None,
    domain=None,
)
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
