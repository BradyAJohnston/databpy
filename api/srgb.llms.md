# srgb

``` python
srgb()
```

A `FLOAT_COLOR` attribute as sRGB RGBA float32 colors.

Blender stores color attributes as linear colors. The values of this array are sRGB, and are converted to linear when they are stored, and from linear when they are read as `bob["name", db.srgb]`. Alpha isn’t converted. Results of math on an `srgb` array are also `srgb` arrays, so that they are still converted when stored, unless the math mixes in another kind of typed array such as `db.color`.

Read colors as `bob["name", db.srgb]` rather than `bob["name"].view(db.srgb)`, which would label linear values as sRGB without converting them.

## Methods

| Name | Description |
|----|----|
| [fill](#databpy.srgb.fill) | Fill the array with a scalar value and sync to Blender. |
| [partition](#databpy.srgb.partition) | Partition the array in-place and sync to Blender. |
| [put](#databpy.srgb.put) | Set values at the given flat indices and sync to Blender. |
| [sort](#databpy.srgb.sort) | Sort the array in-place and sync to Blender. |

### fill

``` python
srgb.fill(value)
```

Fill the array with a scalar value and sync to Blender.

### partition

``` python
srgb.partition(*args, **kwargs)
```

Partition the array in-place and sync to Blender.

### put

``` python
srgb.put(*args, **kwargs)
```

Set values at the given flat indices and sync to Blender.

### sort

``` python
srgb.sort(*args, **kwargs)
```

Sort the array in-place and sync to Blender.
