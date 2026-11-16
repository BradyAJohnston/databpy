# Drawings

``` python
Drawings(grease_pencil, bob=None)
```

The drawings of a grease pencil’s layers, by layer name.

`drawings["Lines"]` is the drawing of the layer “Lines” shown on the scene’s current frame, and `drawings["Lines", 12]` the drawing shown at frame 12, which is the one on the last keyframe at or before it. Iterating gives the names of the layers that have a drawing on the current frame.

Available as `bob.drawings` on a grease pencil object, and as `GeometrySet.drawings` for evaluated geometry, where they are read-only.

## Examples

    bob.drawings["Lines"].point["radius"] = 0.01
    for layer, drawing in bob.drawings.items():
        drawing.point["opacity"] = 0.5
