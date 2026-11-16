# InstanceDomainView

``` python
InstanceDomainView(geometry)
```

Read-only dictionary-style access to the INSTANCE domain of evaluated geometry.

Available on a `GeometrySet` as `instance`. Instance attributes only exist in evaluated geometry, and the values are a copy, so they can be read but not written.

## Examples

    geom = db.GeometrySet(obj)
    geom.instance["instance_transform", db.mat4]
    geom.instance.list_attributes()

## Methods

| Name | Description |
|----|----|
| [list_attributes](#databpy.InstanceDomainView.list_attributes) | List the names of the instance attributes. |

### list_attributes

``` python
InstanceDomainView.list_attributes(drop_hidden=False)
```

List the names of the instance attributes.
