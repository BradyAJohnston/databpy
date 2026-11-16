# Drawing

``` python
Drawing(grease_pencil, key, bob=None)
```

The points and strokes of a grease pencil drawing: one layer on one keyframe.

Get a drawing from `bob.drawings` for a grease pencil object, or from `GeometrySet.drawings` for any object whose evaluated geometry has grease pencil. Its attributes are on the `point` and `curve` domain views, the same as on a `BlenderObject`. Changes to the drawings of a grease pencil object are written back to Blender, while the drawings of evaluated geometry are read-only copies.

The drawing is looked up each time it is used, so a `Drawing`, and arrays read from it, stay valid when keyframes are added. They raise a `LinkedObjectError` once the layer is removed or renamed, or the keyframe is removed or moved to another frame. A keyframe is found by its frame, so if another keyframe is moved onto that frame, its drawing is used instead.

A keyframe made with `frames.copy(..., instance_drawing=True)` shares the drawing of the keyframe it was copied from, so changes to one also change the other.

## Examples

    drawing = bob.drawings["Lines"]
    drawing.point["radius"] *= 0.5
    drawing.curve["material_index"] = 1

## Attributes

| Name | Description |
|----|----|
| [attributes](#databpy.Drawing.attributes) | The attributes collection of the drawing. |
| [curve](#databpy.Drawing.curve) | Attributes on the CURVE domain, one value per stroke. |
| [drawing](#databpy.Drawing.drawing) | The `bpy.types.GreasePencilDrawing` this wraps. |
| [frame](#databpy.Drawing.frame) | The frame of the drawing’s keyframe. |
| [layer](#databpy.Drawing.layer) | The name of the drawing’s layer. |
| [point](#databpy.Drawing.point) | Attributes on the POINT domain. |
| [read_only](#databpy.Drawing.read_only) | Whether this is a drawing of evaluated geometry, which can’t be written. |

## Methods

| Name | Description |
|----|----|
| [list_attributes](#databpy.Drawing.list_attributes) | List the names of the drawing’s attributes. |
| [remove_named_attribute](#databpy.Drawing.remove_named_attribute) | Remove an attribute from the drawing. |
| [store_named_attribute](#databpy.Drawing.store_named_attribute) | Store a named attribute on the drawing, creating it if needed. |

### list_attributes

``` python
Drawing.list_attributes(drop_hidden=False)
```

List the names of the drawing’s attributes.

### remove_named_attribute

``` python
Drawing.remove_named_attribute(name)
```

Remove an attribute from the drawing.

#### Raises

| Name | Type | Description |
|----|----|----|
|  | [TypeError](https://docs.python.org/3/builtins/exceptions.html#TypeError) | If the drawing is from evaluated geometry, which is read-only. |
|  | [AttributeNotFoundError](../api/AttributeNotFoundError.llms.md#databpy.AttributeNotFoundError) | If the attribute doesn’t exist. |
|  | [NamedAttributeError](../api/NamedAttributeError.llms.md#databpy.NamedAttributeError) | If the attribute is required by Blender (e.g. `position`). |

### store_named_attribute

``` python
Drawing.store_named_attribute(data, name, atype=None, domain=None)
```

Store a named attribute on the drawing, creating it if needed.

Takes the same arguments as `BlenderObject.store_named_attribute`. New attributes are stored on the POINT domain unless `domain` is given.

#### Raises

| Name | Type | Description |
|----|----|----|
|  | [TypeError](https://docs.python.org/3/builtins/exceptions.html#TypeError) | If the drawing is from evaluated geometry, which is read-only. |
