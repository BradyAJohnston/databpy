# Grease pencil and evaluated geometry

This guide covers attributes that aren’t stored on an object’s own data-block: the points and strokes of a grease pencil object, which are on its drawings, and the geometry that an object’s modifiers output. It assumes you have read [Attributes](attributes.llms.md). The arrays in this guide sync with Blender as [Syncing with Blender](syncing.llms.md) describes, except that arrays read from evaluated geometry are read-only copies.

## Grease pencil

A grease pencil object has layers, and each layer has keyframes. Each keyframe has a drawing, which holds the points and strokes shown from that frame. The object itself only holds attributes on the `LAYER` domain, with one value for each layer.

[`create_grease_pencil_object()`](api/create_grease_pencil_object.llms.md#databpy.create_grease_pencil_object) creates a grease pencil object with one drawing for each layer, from the positions of each layer’s points and the number of points in each stroke:

``` python
import databpy as db
import numpy as np
import bpy

gp = db.BlenderObject(
    db.create_grease_pencil_object(
        {
            "Lines": (np.random.random((7, 3)), [3, 4]),
            "Outline": (np.random.random((5, 3)), [5]),
        }
    )
)
```

### Store values on each layer

`bob.layer` is the domain view of the `LAYER` domain. `bob.point` and `bob.curve` are empty on a grease pencil object, as its points and strokes are on its drawings:

``` python
gp.layer["weight"] = db.float32(np.array([0.5, 1.0]))
print(len(gp.layer), len(gp.point))
gp.layer["weight"]
```

    2 0

    AttributeArray(name='weight', object='GreasePencil', mesh='GreasePencil', domain=LAYER, type=FLOAT, shape=(2,), dtype=float32)
    array([0.5, 1. ], dtype=float32)

`bob["name"] = values` can’t create an attribute on a grease pencil object, because the `POINT` domain that it stores new attributes on isn’t on the object. It raises a [`NamedAttributeError`](api/NamedAttributeError.llms.md#databpy.NamedAttributeError). Use `bob.layer["name"] = values` for one value for each layer, or a drawing for the points and strokes.

### Store values on points and strokes

`bob.drawings` gives the drawing of each layer, by the layer’s name. A [`Drawing`](api/Drawing.llms.md#databpy.Drawing) has `point` and `curve` domain views, which work like those of an object and write changes back to Blender:

``` python
lines = gp.drawings["Lines"]
lines.point["radius"] = 0.02
lines.curve["material_index"] = 1
print(len(lines.point), len(lines.curve))
lines.point["position"]
```

    7 2

    AttributeArray(name='position', object='GreasePencil', mesh='GreasePencil', domain=POINT, type=FLOAT_VECTOR, shape=(7, 3), dtype=float32)
    array([[0.02171194, 0.8996931 , 0.05696411],
           [0.95113844, 0.46461773, 0.3679338 ],
           [0.44788116, 0.46091697, 0.67438763],
           [0.5939495 , 0.684268  , 0.47139627],
           [0.21098803, 0.35678238, 0.57617986],
           [0.3032536 , 0.77926266, 0.80189574],
           [0.8425829 , 0.17567468, 0.16312881]], dtype=float32)

[`Drawings`](api/Drawings.llms.md#databpy.Drawings) is a mapping, so you can loop over the layers:

``` python
for name, drawing in gp.drawings.items():
    drawing.point["opacity"] = 0.5
list(gp.drawings)
```

    ['Lines', 'Outline']

### Choose a keyframe

`gp.drawings["Lines"]` is the drawing of the layer `"Lines"` shown on the scene’s current frame. When the layer has more than one keyframe, `gp.drawings["Lines", 12]` is the drawing shown at frame 12, which is the drawing of the last keyframe at or before frame 12. Iterating over `bob.drawings` gives the layers that show a drawing on the current frame.

A drawing, and the arrays read from it, keep writing to the same layer and keyframe when the scene’s frame changes or you add keyframes. They raise a [`LinkedObjectError`](api/LinkedObjectError.llms.md#databpy.LinkedObjectError) once the layer is removed or renamed, or the keyframe is removed or moved to another frame. databpy finds the keyframe by its frame number, so if you move another keyframe onto that frame, the drawing of the moved keyframe is used instead. Keyframes copied with `instance_drawing=True` share one drawing, so a change to either one changes both.

## Evaluated geometry

An object’s modifiers, such as Geometry Nodes, output evaluated geometry. Evaluated geometry can hold several components at once: a mesh, a point cloud, curves, grease pencil and instances. [`GeometrySet`](api/GeometrySet.llms.md#databpy.GeometrySet) evaluates an object and gives the attributes of each component:

``` python
geom = db.GeometrySet(bpy.data.objects["Cube"])
print(list(geom.components()))
geom.list_attributes(drop_hidden=True)
```

    ['MESH']

    {'MESH': ['UVMap', 'position', 'sharp_face']}

[`named_attribute()`](api/GeometrySet.llms.md#databpy.GeometrySet.named_attribute) reads an attribute from a component. Without a component, it reads the first component that has the attribute. Pass a typed array as `atype=` to check the type:

``` python
geom.named_attribute("position", component="MESH", atype=db.vec3)
```

    AttributeArray(name='Unknown', object='Unknown', mesh='Unknown', domain=Unknown, type=Unknown, shape=(8, 3), dtype=float32)
    array([[ 1.,  1.,  1.],
           [ 1.,  1., -1.],
           [ 1., -1.,  1.],
           [ 1., -1., -1.],
           [-1.,  1.,  1.],
           [-1.,  1., -1.],
           [-1., -1.,  1.],
           [-1., -1., -1.]], dtype=float32)

The values that a `GeometrySet` gives are copies. Changing them doesn’t change the object, and databpy can’t store attributes on evaluated geometry.

A `GeometrySet` is a snapshot of the evaluated geometry when you create it, so it doesn’t follow later changes to the object. The `GeometrySet` owns its components, such as `geom.mesh`, and frees them when it is deleted. Keep a reference to the `GeometrySet` while you use them: `db.GeometrySet(obj).mesh.vertices` raises a `ReferenceError`, because the `GeometrySet` is deleted before the mesh is used.

### Read instance attributes

Instance attributes only exist in evaluated geometry. [`GeometrySet.instance`](api/GeometrySet.llms.md#databpy.GeometrySet) is a read-only domain view of them, [`InstanceDomainView`](api/InstanceDomainView.llms.md#databpy.InstanceDomainView):

``` python
geom = db.GeometrySet(obj)
geom.instance["instance_transform", db.mat4]
```

### Read grease pencil drawings

Geometry Nodes can output grease pencil from an object of any type, such as with the Curves to Grease Pencil node. That grease pencil only exists in the evaluated geometry. [`GeometrySet.drawings`](api/GeometrySet.llms.md#databpy.GeometrySet) gives read-only access to its drawings, and `named_attribute()` with `component="GREASE_PENCIL"` reads its `LAYER` attributes:

``` python
geom = db.GeometrySet(obj)
geom.drawings["Layer"].point["position"]
```
