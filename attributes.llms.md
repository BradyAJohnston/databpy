# Working with Attributes

# Understanding the Attribute System

## What are Attributes?

In Blender, all data on geometry is stored as **attributes**. An attribute is a named array of values associated with elements of geometry. Every piece of information—vertex positions, edge indices, face normals, UV coordinates, vertex colors—exists as an attribute on a specific **domain**.

For example: - Vertex positions are stored as a `FLOAT_VECTOR` attribute named `"position"` on the `POINT` domain - Face materials are stored as an `INT` attribute on the `FACE` domain - UV maps are stored as `FLOAT2` attributes on the `CORNER` domain

`databpy` provides a clean, intuitive interface for working with these attributes using familiar NumPy operations.

## The Three-Level API

`databpy` offers three levels of abstraction for working with attributes, each suited to different use cases:

``` mermaid
flowchart TD
    A[BlenderObject] --> B[AttributeArray]
    B --> C[Attribute]
    C --> D[bpy.types.Attribute]

    A -.->|"Auto-sync, convenience methods"| E[User Level]
    B -.->|"NumPy operations with auto-sync"| E
    C -.->|"Manual control, one-shot operations"| F[Advanced Use]
    D -.->|"Raw Blender API"| G[Low Level]

    style A fill:#90EE90
    style B fill:#87CEEB
    style C fill:#FFB6C1
    style D fill:#FFE4B5
```

### 1. [`BlenderObject`](api/BlenderObject.llms.md#databpy.BlenderObject) - Highest Level (Most Convenient)

The [`BlenderObject`](api/BlenderObject.llms.md#databpy.BlenderObject) class (nicknamed “bob”) provides the most ergonomic interface with dictionary-style access and convenience properties.

``` python
import databpy as db
import numpy as np

# Create a simple object
bob = db.create_bob(np.random.rand(10, 3))

# Access attributes like a dictionary - returns AttributeArray
positions = bob["position"]
positions[:, 2] += 1.0  # Automatically syncs to Blender

# Or use the convenience property
bob.position[:, 2] += 1.0  # Same thing

# Store new attributes
bob["my_values"] = np.random.rand(10)
```

**When to use:** Interactive work, scripting, when you want automatic syncing.

### 2. [`AttributeArray`](api/AttributeArray.llms.md#databpy.AttributeArray) - Mid Level (Auto-Syncing NumPy)

[`AttributeArray`](api/AttributeArray.llms.md#databpy.AttributeArray) is a [`numpy.ndarray`](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray) subclass that automatically writes changes back to Blender. It provides natural NumPy operations with automatic bidirectional syncing.

``` python
import databpy as db
import bpy

obj = bpy.data.objects["Cube"]

# Create an AttributeArray
pos = db.AttributeArray(obj, "position")

# All NumPy operations work and auto-sync
pos[:, 2] += 1.0      # In-place addition
pos *= 2.0            # Broadcasting
pos[0] = [0, 0, 0]    # Item assignment

# Changes are immediately reflected in Blender
```

> **NOTE:**
>
> `AttributeArray` syncs the **entire** attribute array on every modification, not just changed values. This is due to Blender’s `foreach_set` API. For large meshes (10K+ vertices), consider batching operations or using the lower-level `Attribute` class.

**When to use:** When you need NumPy-like operations with automatic syncing, working with position/color/custom data interactively.

### 3. `Attribute` - Low Level (Manual Control)

The `Attribute` class provides direct, stateless access with explicit control over when data is read or written.

``` python
import databpy as db
import numpy as np
import bpy

obj = bpy.data.objects["Cube"]

# Get the attribute wrapper
attr = db.Attribute(obj.data.attributes["position"])

# Manually read data
positions = attr.as_array()

# Perform operations (no auto-sync)
positions[:, 2] += 1.0
positions *= 2.0

# Manually write back (single write operation)
attr.from_array(positions)
```

**When to use:** - One-shot read or write operations - Performance-critical code where you want control over sync timing - Batch processing where you make many changes before writing back - When you need to inspect attribute metadata without reading data

## Attribute Types

Blender supports various attribute data types. `databpy` works with all of them through the [`AttributeTypes`](api/AttributeTypes.llms.md#databpy.AttributeTypes) enum:

### Float-Based Types

``` python
import databpy as db
import numpy as np

bob = db.create_bob(np.random.rand(10, 3))

# FLOAT - Single float per element
temperatures = np.random.rand(10).astype(np.float32)
bob["temperature"] = temperatures

# FLOAT2 - 2D vectors
uv_coords = np.random.rand(10, 2).astype(np.float32)
db.store_named_attribute(bob.object, uv_coords, "uv", atype="FLOAT2")

# FLOAT_VECTOR - 3D vectors (most common)
velocities = np.random.rand(10, 3).astype(np.float32)
bob["velocity"] = velocities

# FLOAT_COLOR - RGBA colors (4 components)
colors = np.random.rand(10, 4).astype(np.float32)
db.store_named_attribute(bob.object, colors, "color", atype="FLOAT_COLOR")

# QUATERNION - Rotations (4 components: w, x, y, z)
rotations = np.random.rand(10, 4).astype(np.float32)
db.store_named_attribute(bob.object, rotations, "rotation", atype="QUATERNION")

# FLOAT4X4 - 4x4 transformation matrices
matrices = np.random.rand(10, 4, 4).astype(np.float32)
db.store_named_attribute(bob.object, matrices, "transform", atype="FLOAT4X4")
```

    bpy.data.meshes['NewObject.001'].attributes["transform"]

### Integer-Based Types

``` python
# INT - 32-bit signed integers
ids = np.arange(10, dtype=np.int32)
bob["id"] = ids

# INT8 - 8-bit signed integers (memory efficient)
small_values = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], dtype=np.int8)
db.store_named_attribute(bob.object, small_values, "category", atype="INT8")

# INT32_2D - 2D integer vectors
pairs = np.random.randint(0, 100, size=(10, 2), dtype=np.int32)
db.store_named_attribute(bob.object, pairs, "edge_ids", atype="INT32_2D")
```

    bpy.data.meshes['NewObject.001'].attributes["edge_ids"]

### Color Types

``` python
# BYTE_COLOR - RGBA as unsigned 8-bit (0-255)
byte_colors = np.random.randint(0, 255, size=(10, 4), dtype=np.uint8)
db.store_named_attribute(bob.object, byte_colors, "vertex_color", atype="BYTE_COLOR")
```

    bpy.data.meshes['NewObject.001'].attributes["vertex_color"]

### Boolean Type

``` python
# BOOLEAN - True/False flags
selection = np.random.rand(10) > 0.5
bob["selected"] = selection
```

> **TIP:**
>
> If you don’t specify an `atype`, `databpy` will infer it from your array’s dtype and shape using `guess_atype_from_array()`.

## Attribute Domains

Attributes exist on different **domains** of the geometry, specified by the [`AttributeDomains`](api/AttributeDomains.llms.md#databpy.AttributeDomains) enum:

| Domain | Description | Example Use Cases |
|----|----|----|
| `POINT` | Vertices, curve control points | Positions, vertex colors, temperature |
| `EDGE` | Mesh edges | Edge weights, crease values |
| `FACE` | Mesh faces/polygons | Material indices, face areas |
| `CORNER` | Face corners (vertex-face pairs) | UV coordinates, split normals |
| `CURVE` | Individual curve splines | Per-spline properties |
| `INSTANCE` | Geometry instances | Instance transforms, IDs |

``` python
import databpy as db
import numpy as np
import bpy

obj = bpy.data.objects["Cube"]

# POINT domain (default) - one value per vertex
vertex_data = np.random.rand(len(obj.data.vertices), 3)
db.store_named_attribute(obj, vertex_data, "vertex_attr", domain="POINT")

# FACE domain - one value per face
face_data = np.random.rand(len(obj.data.polygons))
db.store_named_attribute(obj, face_data, "face_attr", domain="FACE")

# EDGE domain - one value per edge
edge_data = np.random.rand(len(obj.data.edges))
db.store_named_attribute(obj, edge_data, "edge_attr", domain="EDGE")
```

    bpy.data.meshes['Cube'].attributes["edge_attr"]

> **IMPORTANT:**
>
> The length of your data array must match the number of elements in the target domain. A cube has 8 vertices, 12 edges, and 6 faces, so your arrays must have corresponding lengths.

## Common Workflows

### Reading Attributes

``` python
import databpy as db
import bpy

obj = bpy.data.objects["Cube"]

# Method 1: Simple function call (returns regular numpy array)
positions = db.named_attribute(obj, "position")  # see named_attribute()

# Method 2: Via BlenderObject (returns AttributeArray)
bob = db.BlenderObject(obj)  # see BlenderObject
positions = bob["position"]  # or bob.position

# Method 3: List available attributes
attrs = db.list_attributes(obj)  # see list_attributes()
print(attrs)

# Method 4: With modifier evaluation
evaluated_positions = db.named_attribute(obj, "position", evaluate=True)
```

    ['.corner_edge', '.corner_vert', '.edge_verts', '.select_edge', '.select_poly', '.select_vert', '.uv_select_edge', '.uv_select_face', '.uv_select_vert', 'UVMap', 'edge_attr', 'face_attr', 'position', 'sharp_face', 'vertex_attr']

### Writing Attributes

``` python
import databpy as db
import numpy as np

bob = db.create_bob(np.random.rand(10, 3))

# Method 1: Dictionary-style (most convenient)
bob["my_data"] = np.random.rand(10, 3)

# Method 2: Function call (more options)
db.store_named_attribute(
    bob.object,
    data=np.random.rand(10),
    name="custom_attr",
    atype="FLOAT",
    domain="POINT",
    overwrite=True
)

# Method 3: Via BlenderObject method
bob.store_named_attribute(
    np.random.rand(10, 3),
    name="another_attr",
    domain="POINT"
)
```

### Modifying Attributes In-Place

``` python
import databpy as db
import numpy as np

bob = db.create_bob(np.random.rand(100, 3))

# Using AttributeArray for interactive modifications
pos = bob.position

# Simple operations
pos[:, 2] += 1.0          # Move all points up
pos *= 2.0                # Scale positions
pos[pos < 0] = 0          # Clamp negative values

# Boolean indexing
selection = pos[:, 2] > 0.5
pos[selection, 2] = 1.0

# Column operations
pos[:, 0] = np.linspace(0, 1, len(pos))  # Linear ramp on X
```

### Batch Processing (Performance)

For large datasets, use the `Attribute` class to batch operations:

``` python
import databpy as db
import numpy as np
import bpy

obj = db.create_object(np.random.rand(int(1e5), 3))
attr = db.Attribute(obj.data.attributes["position"])

# Single read
positions = attr.as_array()

# Many operations without syncing
positions[:, 2] += 1.0
positions *= 2.0
positions = np.clip(positions, -10, 10)

# Single write
attr.from_array(positions)
```

> **TIP:**
>
> - `AttributeArray`: ~N writes for N operations (auto-sync each time)
> - `Attribute`: 1 read + 1 write for N operations (manual control)
>
> For 100K vertices with 10 operations, `Attribute` can be 10x faster.

### Working with Integer Attributes

``` python
import databpy as db
import numpy as np

bob = db.create_bob(np.random.rand(10, 3))

# Store integer IDs
ids = np.arange(10, dtype=np.int32)
bob["id"] = ids

# Retrieve as AttributeArray
id_array = bob["id"]

# Modify (automatically maintains int32 dtype)
id_array += 100

# Verify it's still integers
print(id_array.dtype)  # int32
```

    int32

### Working with Boolean Attributes

``` python
import databpy as db
import numpy as np

bob = db.create_bob(np.random.rand(20, 3))

# Create selection based on position
selection = bob.position[:, 2] > 0.5
bob["selected"] = selection

# Use boolean attribute for filtering
selected_mask = bob["selected"]
bob.position[selected_mask, 2] = 1.0
```

## Error Handling

`databpy` uses a consistent exception hierarchy for attribute-related errors:

### Exception Hierarchy

- **`db.NamedAttributeError`** (base class, inherits from `AttributeError`)
  - Raised when attribute operations fail
  - Used for: non-existent attributes, invalid names, domain size mismatches
  - **`db.AttributeMismatchError`** (inherits from `NamedAttributeError`)
    - Raised when data doesn’t match attribute expectations
    - Used for: shape mismatches, type incompatibilities

### Common Error Scenarios

``` python
import databpy as db
import numpy as np
import bpy

obj = bpy.data.objects["Cube"]

try:
    # Trying to access non-existent attribute
    data = db.named_attribute(obj, "nonexistent")
except db.NamedAttributeError as e:
    print(f"Attribute not found: {e}")

try:
    # Wrong data size for domain
    db.store_named_attribute(obj, np.random.rand(100, 3), "test")
except db.NamedAttributeError as e:
    print(f"Size mismatch: {e}")

try:
    # Shape mismatch when using Attribute class
    attr = db.Attribute(obj.data.attributes["position"])
    wrong_shape = np.random.rand(8, 4)  # Should be (8, 3)
    attr.from_array(wrong_shape)
except db.AttributeMismatchError as e:
    print(f"Shape error: {e}")
```

    Attribute not found: The selected attribute 'nonexistent' does not exist on the mesh.
    Size mismatch: Data size 300 (shape (100, 3)) does not match the required size 24 for domain `POINT` with 8 elements and dimensions (3,)
    Shape error: Array size 32 does not match attribute size 24. Array shape (8, 4) cannot be reshaped to attribute shape (8, 3)

> **TIP:**
>
> Since `AttributeMismatchError` inherits from `NamedAttributeError`, you can catch all attribute-related errors with a single `except db.NamedAttributeError:` clause.

## Best Practices

### 1. Choose the Right Abstraction Level

- **Interactive work, scripting**: Use `BlenderObject` and `AttributeArray`
- **Performance-critical code**: Use `Attribute` with manual read/write
- **Quick one-off reads**: Use `named_attribute()` function

### 2. Be Mindful of Data Types

``` python
# Good: Explicit dtype matching Blender's storage
data = np.random.rand(10, 3).astype(np.float32)

# Less good: float64 will be converted to float32 anyway
data = np.random.rand(10, 3)  # defaults to float64
```

### 3. Batch Operations When Possible

``` python
# Not great: Multiple syncs
pos = bob.position
for i in range(len(pos)):
    pos[i, 2] += 1.0  # Syncs every iteration!

# Better: Vectorized operation (single sync)
pos[:, 2] += 1.0
```

### 4. Use Named Constants for Domains and Types

``` python
from databpy import AttributeDomains, AttributeTypes

# More readable and type-safe
db.store_named_attribute(
    obj,
    np.random.rand(len(obj.data.vertices), 3),
    "my_attr",
    atype=AttributeTypes.FLOAT_VECTOR,
    domain=AttributeDomains.POINT
)
db.named_attribute(obj, "my_attr")
```

    array([[0.1533536 , 0.21215643, 0.9233092 ],
           [0.46108934, 0.5014878 , 0.22106937],
           [0.9631015 , 0.9697326 , 0.5646438 ],
           [0.64606196, 0.34929293, 0.4942358 ],
           [0.37640113, 0.16596128, 0.7019844 ],
           [0.76804173, 0.1807008 , 0.6537381 ],
           [0.9969051 , 0.06999371, 0.6443076 ],
           [0.11305335, 0.7311435 , 0.05457871]], dtype=float32)

### 5. Clean Up Temporary Attributes

``` python
# Remove attributes you no longer need
db.remove_named_attribute(obj, "my_attr")
try:
    db.named_attribute(obj, "my_attr")
except db.NamedAttributeError as e:
    print(e)
```

    The selected attribute 'my_attr' does not exist on the mesh.

## Architecture Summary

Understanding the relationship between the classes helps you choose the right tool:

    ┌─────────────────────────────────────────────────────┐
    │ BlenderObject (bob)                                 │
    │ - High-level convenience wrapper                    │
    │ - Dictionary access: bob["attr"]                    │
    │ - Property access: bob.position                     │
    │ - Returns: AttributeArray                           │
    └─────────────────┬───────────────────────────────────┘
                      │
                      │ creates/returns
                      ▼
    ┌─────────────────────────────────────────────────────┐
    │ AttributeArray                                      │
    │ - NumPy subclass with auto-sync                     │
    │ - All NumPy operations work                         │
    │ - Syncs entire array on every modification          │
    │ - References: Attribute (for metadata)              │
    └─────────────────┬───────────────────────────────────┘
                      │
                      │ uses
                      ▼
    ┌─────────────────────────────────────────────────────┐
    │ Attribute                                           │
    │ - Low-level wrapper, manual control                 │
    │ - Methods: as_array(), from_array()                 │
    │ - Properties: atype, domain, shape, dtype           │
    │ - One-shot reads/writes                             │
    └─────────────────┬───────────────────────────────────┘
                      │
                      │ wraps
                      ▼
    ┌─────────────────────────────────────────────────────┐
    │ bpy.types.Attribute                                 │
    │ - Raw Blender API                                   │
    │ - foreach_get/foreach_set                           │
    └─────────────────────────────────────────────────────┘

## See Also

### Core Classes

- [`BlenderObject`](api/BlenderObject.llms.md#databpy.BlenderObject) - High-level object wrapper with convenience methods
- [`AttributeArray`](api/AttributeArray.llms.md#databpy.AttributeArray) - Auto-syncing NumPy array subclass
- `Attribute` - Low-level attribute wrapper with manual control

### Functions

- [`named_attribute()`](api/named_attribute.llms.md#databpy.named_attribute) - Read attribute data as NumPy array
- [`store_named_attribute()`](api/store_named_attribute.llms.md#databpy.store_named_attribute) - Write attribute data to object
- [`remove_named_attribute()`](api/remove_named_attribute.llms.md#databpy.remove_named_attribute) - Delete an attribute
- `list_attributes()` - List all attributes on an object
- [`create_bob()`](api/create_bob.llms.md#databpy.create_bob) - Create a new BlenderObject
- [`create_object()`](api/create_object.llms.md#databpy.create_object) - Create a new Blender object

### Type Enums

- [`AttributeTypes`](api/AttributeTypes.llms.md#databpy.AttributeTypes) - Enum of all available attribute data types
- [`AttributeDomains`](api/AttributeDomains.llms.md#databpy.AttributeDomains) - Enum of all available geometry domains

### Exceptions

- `NamedAttributeError` - Base exception for attribute operations
- `AttributeMismatchError` - Exception for data/type mismatches

### External References

- [`numpy.ndarray`](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray) - NumPy array documentation
- [`bpy.types.Object`](https://docs.blender.org/api/current/bpy.types.Object.html#bpy.types.Object) - Blender Object documentation
- [`bpy.types.Attribute`](https://docs.blender.org/api/current/bpy.types.Attribute.html#bpy.types.Attribute) - Blender Attribute documentation
