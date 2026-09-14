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
| [GeometrySet](../api/GeometrySet.llms.md#databpy.GeometrySet) | Access the evaluated geometry of an object (`bpy.types.GeometrySet`). |
| [BlenderObject](../api/BlenderObject.llms.md#databpy.BlenderObject) | A convenience class for working with Blender objects. |
| [BlenderObjectAttribute](../api/BlenderObjectAttribute.llms.md#databpy.BlenderObjectAttribute) | Minimal base class for Blender objects with attribute access. |
| [BlenderObjectBase](../api/BlenderObjectBase.llms.md#databpy.BlenderObjectBase) | Minimal base class for Blender objects with name and object access. |
| [LinkedObjectError](../api/LinkedObjectError.llms.md#databpy.LinkedObjectError) | Error raised when a Python object doesn’t have a linked object in the 3D scene. |

## Utilities

Typed helpers that check for None or narrow data-block types, plus general utilities

|  |  |
|----|----|
| [require](../api/require.llms.md#databpy.require) | Return the given value, raising an error if it is None. |
| [require_data](../api/require_data.llms.md#databpy.require_data) | Return the object’s data-block, checked to be of the given type. |
| [mesh_data](../api/mesh_data.llms.md#databpy.mesh_data) | Return the object’s data-block, checked to be a `Mesh`. |
| [curves_data](../api/curves_data.llms.md#databpy.curves_data) | Return the object’s data-block, checked to be a `Curves`. |
| [pointcloud_data](../api/pointcloud_data.llms.md#databpy.pointcloud_data) | Return the object’s data-block, checked to be a `PointCloud`. |
| [volume_data](../api/volume_data.llms.md#databpy.volume_data) | Return the object’s data-block, checked to be a `Volume`. |
| [active_scene](../api/active_scene.llms.md#databpy.active_scene) | Return the active scene, raising an error if there is none. |
| [active_object](../api/active_object.llms.md#databpy.active_object) | Return the active object, raising an error if there is none. |
| [centre](../api/centre.llms.md#databpy.centre) | Calculate the weighted centroid of the vectors. |
| [lerp](../api/lerp.llms.md#databpy.lerp) | Linearly interpolate between two values. |

## Nodes

Helpers for building and manipulating geometry node trees

|  |  |
|----|----|
| [nodes.new_tree](../api/nodes.new_tree.llms.md#databpy.nodes.new_tree) |  |
| [nodes.swap_tree](../api/nodes.swap_tree.llms.md#databpy.nodes.swap_tree) |  |
| [nodes.custom_string_iswitch](../api/nodes.custom_string_iswitch.llms.md#databpy.nodes.custom_string_iswitch) | Creates a node group containing a `Index Switch` node with all the given values. |
| [nodes.append_from_blend](../api/nodes.append_from_blend.llms.md#databpy.nodes.append_from_blend) | Append a Geometry Nodes node tree from the given .blend file |
| [nodes.new_socket](../api/nodes.new_socket.llms.md#databpy.nodes.new_socket) | Create a new input or output socket on the interface of the node tree. |
| [nodes.tree_interface](../api/nodes.tree_interface.llms.md#databpy.nodes.tree_interface) | Return the interface of a node tree, raising an error if it has none. |
| [nodes.input_socket](../api/nodes.input_socket.llms.md#databpy.nodes.input_socket) | Get an input socket of a node by index or name. |
| [nodes.output_socket](../api/nodes.output_socket.llms.md#databpy.nodes.output_socket) | Get an output socket of a node by index or name. |
| [nodes.socket_value](../api/nodes.socket_value.llms.md#databpy.nodes.socket_value) | Return the default value of a socket. |
| [nodes.set_socket_value](../api/nodes.set_socket_value.llms.md#databpy.nodes.set_socket_value) | Set the default value of a socket. |
| [nodes.MaintainConnections](../api/nodes.MaintainConnections.llms.md#databpy.nodes.MaintainConnections) |  |
| [nodes.DuplicatePrevention](../api/nodes.DuplicatePrevention.llms.md#databpy.nodes.DuplicatePrevention) | Context manager to cleanup duplicated node trees when appending node groups |
