# nodes.tree_interface

``` python
nodes.tree_interface(tree)
```

Return the interface of a node tree, raising an error if it has none.

`NodeTree.interface` is typed as optional in the Blender API, but a valid node group always has one, so this narrows the type for further use.
