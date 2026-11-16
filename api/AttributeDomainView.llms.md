# AttributeDomainView

``` python
AttributeDomainView(bob, domain)
```

Dictionary-style access to the attributes on a single domain of an object.

Available on a `BlenderObject` as `point`, `edge`, `face`, `corner`, `curve` and `layer`, and on a grease pencil `Drawing` as `point` and `curve`. New attributes are stored on this domain, with their type inferred from the data.

## Examples

    bob.face["area"] = np.ones(len(bob.face))
    bob.face["area"]  # AttributeArray of the face values
    bob.face.list_attributes()

## Methods

| Name | Description |
|----|----|
| [list_attributes](#databpy.AttributeDomainView.list_attributes) | List the names of the attributes on this domain. |

### list_attributes

``` python
AttributeDomainView.list_attributes(drop_hidden=False)
```

List the names of the attributes on this domain.
