# Changelog

## 0.10.0 (unreleased)

A robustness release, in preparation for wider use of databpy across projects. Node related functionality is deprecated in favour of [nodebpy](https://pypi.org/project/nodebpy/), objects are tracked in a way that survives renames, reallocation and other add-ons, and attribute data is validated instead of being silently corrupted.

databpy follows semantic versioning. Deprecated functionality raises a `FutureWarning` and is kept for at least two minor releases before removal. Everything deprecated in this release is removed in 0.12.0.

### Deprecated

- `databpy.nodes`: `new_tree`, `swap_tree`, `custom_string_iswitch`, `append_from_blend`, `DuplicatePrevention`, `cleanup_duplicates`, `deduplicate_node_trees`, `get_input`, `get_output`, `MaintainConnections`, `tree_interface`, `new_socket`, `input_socket`, `output_socket`, `socket_value` and `set_socket_value`. Node functionality is moving to nodebpy.
- `register()` is no longer required. `unregister()` is now a no-op: it previously removed `Object.uuid`, which broke every other add-on using databpy.
- The registered `Object.uuid` property. The uuid is now stored as the custom property `obj["_databpy_uuid"]`, which needs no registration. `Object.uuid` is kept in sync and values from existing .blend files are migrated automatically.
- `NamedAttributeError` subclassing `AttributeError`, as `hasattr()` and `getattr()` silently swallow it. Catch `NamedAttributeError` or `DatabpyError` instead.

### Added

- `DatabpyError`, the base class for all databpy errors.
- `AttributeNotFoundError`, raised for missing attributes. It is both a `NamedAttributeError` and a `KeyError`, and its message lists the available attributes.
- `get_from_uuid(name_hint=...)`, to choose between duplicated objects that share a uuid.
- `py.typed`, so type checkers use databpy’s type hints.

### Changed

- `BlenderObject` tracks its object by `session_uid` within a session, surviving renames and memory reallocation, and by its persistent uuid after a file is loaded. As before, a wrapper stops resolving its object once another wrapper stores a different uuid on it.
- **Breaking**: accessing a `BlenderObject` whose object was removed raises `LinkedObjectError`, instead of resolving to a duplicate that shares its uuid.
- `databpy.object.get_uuid()` / `set_uuid()` read and write the new custom property, falling back to and keeping in sync the registered `Object.uuid` property.
- `AttributeArray` tracks its object by `session_uid` instead of holding a direct reference. Syncing raises `LinkedObjectError` if the object was removed or a file was loaded, instead of warning or writing to stale data.
- `AttributeArray` syncs every in-place modification: all in-place operators, `out=`, `ufunc.at`, `fill`, `sort`, `put`, `partition`, `np.copyto`, `np.place`, `np.putmask` and `np.fill_diagonal`. Augmented assignment on a view (`pos[:, 2] += 1`) writes to Blender once instead of twice.
- **Breaking**: the `domain` argument of `store_named_attribute()` defaults to `None`, using the domain of an existing attribute, otherwise `POINT`. A `domain` that doesn’t match an existing attribute raises `NamedAttributeError` instead of being ignored.
- Writing to an existing attribute without `atype` uses the attribute’s type, instead of raising if the guessed type differed.
- **Breaking**: 1D unsigned integer arrays are stored as `INT` (`uint8` was stored as `INT8`, wrapping values above 127) and `(n, 2)` unsigned arrays as `INT32_2D`.
- **Breaking**: attribute type guessing raises `ValueError` when no type matches (0-d, `(n, 5)`, `(n, 2)` bool, complex or non-numeric multi-column arrays), instead of falling back to `FLOAT`.
- **Breaking**: values that can’t be represented by an integer attribute (overflow, NaN or inf) and complex data raise `AttributeMismatchError`, instead of being silently wrapped or truncated.
- **Breaking**: removing a required attribute such as `position` raises `NamedAttributeError` instead of Blender’s `RuntimeError`.
- `bob["name"]`, `named_attribute()`, `remove_named_attribute()`, `AttributeArray()` and `GeometrySet.named_attribute()` raise `AttributeNotFoundError` for missing attributes. `bob["name"]` previously raised a bare `KeyError`, which it remains a subclass of.
- `store_named_attribute()` and `Attribute.from_array()` accept any array-like data.
- `create_pointcloud_object()` creates the point cloud directly instead of converting a mesh with an operator, so it no longer depends on the context. The `.selection` attribute added by the conversion is no longer present.
- `create_curves_object()` raises `ValueError` if only one of `positions` and `curve_sizes` is given, instead of creating an empty object.
- `create_mesh_object()` and `BlenderObject.new_from_pydata()` raise `ValueError` for out of range edge or face indices, instead of creating an invalid mesh.
- `ObjectTracker` identifies new objects by `session_uid`. `new_objects()` is ordered from oldest to newest and `latest()` returns the most recently created object.
- Object data is refreshed with `update_tag()` after writing attributes, replacing the workaround of reassigning a vertex position.
- The string attribute warning points at the calling code, so it is shown once per call site.
- `AttributeArray` no longer has the private `_attribute` and `_attr_name` attributes. `_blender_object` is kept as a read-only lookup.

### Fixed

- In-place operations other than `+=`, `-=`, `*=` and `/=` modified an `AttributeArray` without syncing to Blender.
- Writing attributes to empty geometry raised `IndexError` or `KeyError`.
- `create_pointcloud_object()` returned a mesh when given a collection not linked to the scene, and left an orphan mesh behind.
- `create_mesh_object()` raised for faces with different numbers of vertices.
- `BlenderObject.centroid()` ignored boolean masks and unsigned index arrays, returning the unweighted centroid. Unsupported dtypes now raise `TypeError`.
- `ObjectTracker` reported renamed objects as new.
- After a uuid mismatch, every access of `BlenderObject.object` searched all objects.

## 0.9.0 (2026-09-14)

A full static-typing pass over the package and test suite. The code base now passes [ty](https://docs.astral.sh/ty/) with zero errors and zero suppression comments (every `# type: ignore` has been removed), and ty runs in CI alongside ruff. Blender API values that are typed as `Something | None` or as wide data-block unions are now handled through small helpers that check at runtime and narrow the type, instead of being ignored.

### Added

- Typed narrowing helpers, exported from the top-level `databpy` namespace:
  - `require()` — return a value, raising `ValueError` if it is `None`
  - `require_data()`, `mesh_data()`, `curves_data()`, `pointcloud_data()`, `volume_data()` — return `Object.data` checked to be the expected data-block type, raising `TypeError` otherwise
  - `active_scene()` and `active_object()` — non-optional accessors for `bpy.context.scene` / `bpy.context.active_object`
- Node helpers in `databpy.nodes` for the optional-heavy node APIs: `tree_interface()`, `new_socket()`, `input_socket()`, `output_socket()`, `socket_value()` and `set_socket_value()`.
- `databpy.object.get_uuid()` / `set_uuid()` for the dynamically registered `uuid` property on `bpy.types.Object`.
- Type checking with ty in CI (new `typecheck` job in the lint workflow), with `ty` and `ruff` added as locked dev dependencies.
- API documentation sections for the new utility and node helpers.

### Changed

- **Breaking**: invalid-type errors now consistently raise `TypeError` (some previously raised `ValueError` or `AttributeError`): `utils.path_resolve()`, `attribute.guess_atype_from_array()`, `BlenderObject.__getitem__()` with a non-string key, assigning a non-`Object` to `BlenderObjectBase.object`, and the deprecated `vertices` / `edges` properties on non-mesh objects.
- Object creation functions (`create_object()`, `create_mesh_object()`, `create_curves_object()`, `create_pointcloud_object()`, `create_bob()` and the `BlenderObject.from_*()` classmethods) are now typed to accept any array-like (lists and tuples always worked at runtime).
- `utils.lerp()` accepts scalars and array-likes, converting to numpy arrays internally (the documented list example now actually works).
- `Attribute()` accepts any `bpy.types.Attribute` and validates it against the supported concrete attribute types, raising `NamedAttributeError` for unsupported ones.
- `nodes.new_tree()` is typed as returning a `GeometryNodeTree` and raises `NodeGroupCreationError` if an existing node group with the requested name is not a geometry node tree.
- `nodes.MaintainConnections` and `nodes.swap_tree()` raise `TypeError` when given a node that is not a `GeometryNodeGroup`.
- `custom_string_iswitch()` catches specific exception types during node group creation (rather than a blind `except Exception`) and chains the original error onto the raised `NodeGroupCreationError`.

### Fixed

- `from databpy import utils` was shadowed by `databpy.nodes.utils` in the package namespace, so static analysis (and potentially import order) resolved `databpy.utils` to the wrong module.
- Docs builds failed with the latest griffe (quartodoc 0.11.1 is incompatible with griffe 2.x); griffe is now pinned to `<2` in the dev dependencies.

## 0.8.0 (2026-07-21)

Support for the new attribute types introduced in Blender 5.2, alongside a cleanup of the attribute typing system. Requires `bpy >= 5.2`.

### Added

- Support for the new Blender 5.2 attribute types:
  - `FLOAT4` — 4D float vectors ([`Float4Attribute`](https://docs.blender.org/api/current/bpy.types.Float4Attribute.html))
  - `INT16_2D` — 2D 16-bit signed integer vectors ([`Short2Attribute`](https://docs.blender.org/api/current/bpy.types.Short2Attribute.html))
  - `STRING` — text strings ([`StringAttribute`](https://docs.blender.org/api/current/bpy.types.StringAttribute.html)). String support is *experimental* and raises a warning when used: string attributes are accessible through the Python API but are not yet properly supported within Geometry Nodes. Values are read and written per-element (as unicode numpy arrays) since Blender’s `foreach_get`/`foreach_set` do not support string properties.
- `GeometrySet`, for accessing all components of an object’s evaluated geometry — including multi-component Geometry Nodes outputs (mesh, point cloud, curves and instances) that a normally evaluated object doesn’t expose. Provides `named_attribute()` / `list_attributes()` across components and an informative `repr()` suited to snapshot testing.
- `Attribute.storage_type`, exposing Blender 5.2’s new attribute storage types (`"ARRAY"` or `"SINGLE"`). `SINGLE`-storage attributes (produced by Geometry Nodes for constant values) read transparently as full arrays.
- `named_attribute(evaluate=True)` and `evaluate_object()` now work for Curves and PointCloud objects, not just meshes.
- `BlenderObject.store_named_attribute()` now returns the created or modified attribute (previously returned `None`).

### Changed

- Results of `AttributeArray` operations (e.g. `pos + 1`, comparisons) are now plain `numpy.ndarray`s, and copies (`pos.copy()`, boolean-mask indexing) are detached from Blender — neither syncs back on modification. True views (slices, column access) remain connected and continue to auto-sync.
- Data is cast to the attribute’s storage dtype before writing, letting Blender’s `foreach_set` use its fast buffer path instead of per-element iteration (a significant speedup for the common case of passing float64 arrays).
- **Breaking**: attribute type guessing for `(n, 4)` float arrays now maps to the generic `FLOAT4` type instead of `FLOAT_COLOR`. To store colors or quaternions, explicitly request them with e.g. `store_named_attribute(..., atype="FLOAT_COLOR")`. `(n, 4)` `uint8` arrays still map to `BYTE_COLOR`.
- Attribute type guessing for `(n, 2)` `int16` / `uint16` arrays now maps to `INT16_2D` (other integer widths still map to `INT32_2D`), and string arrays map to `STRING`.
- Requires `bpy >= 5.2` (previously `>= 5.1`).
- Improved type hints throughout the attribute module: precise `Literal` types for attribute type and domain names, `tuple[int, ...]` shapes, and an immutable `AttributeType` dataclass.

### Fixed

- Setting an existing attribute with dictionary syntax (`bob["color"] = data`) no longer performs a second, redundant write with a re-guessed attribute type, which could raise a type mismatch error for color and quaternion attributes.
- `Attribute.from_array()` now triggers the same object-data refresh workaround as `store_named_attribute()`, so writes through the low-level interface update reliably in the viewport.
- `repr()` of an `AttributeArray` that has lost its attribute reference no longer raises an error.

### Removed

- **Breaking**: removed the unused legacy `AttributeTypeInfo` and `AttributeDomain` classes from the public API. Use the `AttributeTypes` and `AttributeDomains` enums instead.

## 0.7.0 (2026-03-05)

- Updated dependencies for Blender 5.1 ([\#69](https://github.com/BradyAJohnston/databpy/pull/69)).

## 0.6.2 (2026-03-05)

- Improved typing for the attribute module ([\#67](https://github.com/BradyAJohnston/databpy/pull/67)).
- Added `move_to_collection()` for moving objects from one collection into another ([\#62](https://github.com/BradyAJohnston/databpy/pull/62), thanks [@kolibril13](https://github.com/kolibril13)).

## 0.6.0 (2025-11-25)

- Refactored object classes around a more minimal `BlenderObjectBase` ([\#61](https://github.com/BradyAJohnston/databpy/pull/61), [\#63](https://github.com/BradyAJohnston/databpy/pull/63)).

## 0.5.1 (2025-11-06)

- General cleanup ([\#58](https://github.com/BradyAJohnston/databpy/pull/58)).
- Improved deduplication method ([\#60](https://github.com/BradyAJohnston/databpy/pull/60)).

## 0.5.0 (2025-10-25)

- Better point cloud and curves support ([\#57](https://github.com/BradyAJohnston/databpy/pull/57)).
- Requires Blender \>= 4.5 for compatibility with point cloud support.

## 0.4.2 (2025-10-24)

- Internal improvements and cleanup ([\#56](https://github.com/BradyAJohnston/databpy/pull/56)).
- Deprecated `Attribute.n_values` in favor of `Attribute.size`.

## 0.4.1 (2025-10-21)

- Fixed `AttributeArray.__str__` ([\#55](https://github.com/BradyAJohnston/databpy/pull/55)).

## 0.4.0 (2025-10-21)

- Fixed integer attribute returns to be `int32` ([\#54](https://github.com/BradyAJohnston/databpy/pull/54)).

------------------------------------------------------------------------

For older releases, see the [GitHub releases page](https://github.com/BradyAJohnston/databpy/releases).
