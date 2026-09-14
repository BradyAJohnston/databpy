# nodes.new_socket

``` python
nodes.new_socket(tree, name, in_out='INPUT', socket_type='NodeSocketGeometry')
```

Create a new input or output socket on the interface of the node tree.

## Parameters

| Name | Type | Description | Default |
|----|----|----|----|
| tree | `bpy`.[types](https://docs.blender.org/api/current/bpy.types.html#module-bpy.types).[NodeTree](https://docs.blender.org/api/current/bpy.types.NodeTree.html#bpy.types.NodeTree) | The node tree to add the socket to. | *required* |
| name | [str](https://docs.python.org/3/builtins/stdtypes.html#str) | The name of the new socket. | *required* |
| in_out | [Literal](https://docs.python.org/3/library/typing.html#typing.Literal)\['INPUT', 'OUTPUT'\] | Whether the socket is an input or an output. Defaults to “INPUT”. | `'INPUT'` |
| socket_type | [str](https://docs.python.org/3/builtins/stdtypes.html#str) | The socket idname, e.g. “NodeSocketFloat”. Defaults to “NodeSocketGeometry”. | `'NodeSocketGeometry'` |

## Returns

| Name | Type | Description |
|----|----|----|
|  | `bpy`.[types](https://docs.blender.org/api/current/bpy.types.html#module-bpy.types).[NodeTreeInterfaceSocket](https://docs.blender.org/api/current/bpy.types.NodeTreeInterfaceSocket.html#bpy.types.NodeTreeInterfaceSocket) | The newly created socket. |
