# Function reference

## Attribute

For interacting with attributes on meshes

|  |  |
|----|----|
| [named_attribute](../api/named_attribute.llms.md#databpy.named_attribute) | Get the named attribute data from the object. |
| [store_named_attribute](../api/store_named_attribute.llms.md#databpy.store_named_attribute) | Adds and sets the values of an attribute on the object. |
| [remove_named_attribute](../api/remove_named_attribute.llms.md#databpy.remove_named_attribute) | Remove a named attribute from an object. |
| [AttributeDomains](../api/AttributeDomains.llms.md#databpy.AttributeDomains) | Enumeration of attribute domains in Blender. You can store an attribute onto one of |
| [AttributeTypes](../api/AttributeTypes.llms.md#databpy.AttributeTypes) | Enumeration of attribute types in Blender. |
| [AttributeArray](../api/AttributeArray.llms.md#databpy.AttributeArray) | A numpy array subclass that automatically syncs changes back to the Blender object. |

## Collections

Working with collections in Blender

|  |  |
|----|----|
| [create_collection](../api/create_collection.llms.md#databpy.create_collection) | Create a new Blender collection or retrieve an existing one. |
| [move_to_collection](../api/move_to_collection.llms.md#databpy.move_to_collection) | Move one or many objects into a target collection. |

## Objects

|  |  |
|----|----|
| [create_object](../api/create_object.llms.md#databpy.create_object) | Create a new Blender mesh object. |
| [create_mesh_object](../api/create_mesh_object.llms.md#databpy.create_mesh_object) | Create a new Blender mesh object. |
| [create_curves_object](../api/create_curves_object.llms.md#databpy.create_curves_object) | Create a new Blender curves object (new Curves type, not legacy Curve). |
| [create_pointcloud_object](../api/create_pointcloud_object.llms.md#databpy.create_pointcloud_object) | Create a new Blender point cloud object. |
| [create_bob](../api/create_bob.llms.md#databpy.create_bob) | Create a BlenderObject wrapper around a new Blender mesh object. |
| [evaluate_object](../api/evaluate_object.llms.md#databpy.evaluate_object) | Return an object which has the modifiers evaluated. |
| [BlenderObject](../api/BlenderObject.llms.md#databpy.BlenderObject) | A convenience class for working with Blender objects. |
| [BlenderObjectAttribute](../api/BlenderObjectAttribute.llms.md#databpy.BlenderObjectAttribute) | Minimal base class for Blender objects with attribute access. |
| [BlenderObjectBase](../api/BlenderObjectBase.llms.md#databpy.BlenderObjectBase) | Minimal base class for Blender objects with name and object access. |
| [LinkedObjectError](../api/LinkedObjectError.llms.md#databpy.LinkedObjectError) | Error raised when a Python object doesn’t have a linked object in the 3D scene. |
