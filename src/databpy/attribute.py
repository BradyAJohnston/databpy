import ctypes
import math
import os
import warnings
from dataclasses import dataclass
from enum import Enum
from typing import Literal, cast

import bpy
import numpy as np
import numpy.typing as npt
from bpy.types import Object

from ._deprecation import REMOVAL_VERSION
from .errors import DatabpyError

COMPATIBLE_TYPES = [bpy.types.Mesh, bpy.types.Curves, bpy.types.PointCloud]
AttributeDataBlock = bpy.types.Mesh | bpy.types.Curves | bpy.types.PointCloud
# a lazily evaluated alias, as Float4Attribute only exists from Blender 5.2
type PossibleAttributeTypes = (
    bpy.types.IntAttribute
    | bpy.types.BoolAttribute
    | bpy.types.Int2Attribute
    | bpy.types.Short2Attribute
    | bpy.types.FloatAttribute
    | bpy.types.Float2Attribute
    | bpy.types.Float4Attribute
    | bpy.types.ByteIntAttribute
    | bpy.types.Float4x4Attribute
    | bpy.types.ByteColorAttribute
    | bpy.types.FloatColorAttribute
    | bpy.types.QuaternionAttribute
    | bpy.types.FloatVectorAttribute
    | bpy.types.StringAttribute
)
DomainNames = Literal["POINT", "EDGE", "FACE", "CORNER", "CURVE", "INSTANCE", "LAYER"]
StorageTypeNames = Literal["ARRAY", "SINGLE"]
AttributeTypeNames = Literal[
    "FLOAT",
    "FLOAT_VECTOR",
    "FLOAT2",
    "FLOAT4",
    "FLOAT_COLOR",
    "BYTE_COLOR",
    "QUATERNION",
    "INT",
    "INT8",
    "INT16_2D",
    "INT32_2D",
    "FLOAT4X4",
    "BOOLEAN",
    "STRING",
]


class NamedAttributeError(DatabpyError, AttributeError):
    """
    Base exception for all attribute-related errors in databpy.

    Raised when an operation on a named attribute fails, such as data that doesn't
    match the size of the domain, a conflict with the type or domain of an existing
    attribute, or an attribute that can't be created. Subclasses cover a missing
    attribute (`AttributeNotFoundError`) and values that don't fit the attribute
    (`AttributeMismatchError`).

    Notes
    -----
    This currently also subclasses `AttributeError`, which will be removed in databpy
    0.13.0 as `hasattr()` and `getattr()` silently swallow `AttributeError`. Catch
    `NamedAttributeError` or `DatabpyError` instead.
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message


class AttributeNotFoundError(NamedAttributeError, KeyError):
    """
    Exception raised when a named attribute doesn't exist.

    This is also a `KeyError`, so dictionary-style access such as `bob["name"]` can
    be handled like any other missing key.
    """


def _attribute_data(obj: Object) -> AttributeDataBlock:
    """Return the object's data-block, checked to be a type that holds attributes."""
    data = obj.data
    if not isinstance(data, (bpy.types.Mesh, bpy.types.Curves, bpy.types.PointCloud)):
        raise TypeError(
            f"The object is not a compatible type.\n- Obj: {obj}\n- Compatible Types: {COMPATIBLE_TYPES}"
        )
    return data


def _check_obj_attributes(obj: Object) -> None:
    if not isinstance(obj, bpy.types.Object):
        raise TypeError(f"Object must be a bpy.types.Object, not {type(obj)}")
    _attribute_data(obj)


# the FLOAT4 attribute type was added in Blender 5.2
HAS_FLOAT4 = hasattr(bpy.types, "Float4Attribute")

# looking up classes on `bpy.types` is slow, so they are only looked up once
_TYPED_ATTRIBUTES = (
    bpy.types.IntAttribute,
    bpy.types.BoolAttribute,
    bpy.types.Int2Attribute,
    bpy.types.Short2Attribute,
    bpy.types.FloatAttribute,
    bpy.types.Float2Attribute,
    bpy.types.ByteIntAttribute,
    bpy.types.Float4x4Attribute,
    bpy.types.ByteColorAttribute,
    bpy.types.FloatColorAttribute,
    bpy.types.QuaternionAttribute,
    bpy.types.FloatVectorAttribute,
    bpy.types.StringAttribute,
)
_FLOAT4_ATTRIBUTE = bpy.types.Float4Attribute if HAS_FLOAT4 else None


def _as_typed_attribute(attribute: bpy.types.Attribute) -> PossibleAttributeTypes:
    """Narrow a generic `Attribute` to one of the concrete attribute types.

    The concrete subclasses are the ones that expose the `data` collection used
    for reading and writing values.
    """
    if isinstance(attribute, _TYPED_ATTRIBUTES):
        return attribute
    if _FLOAT4_ATTRIBUTE is not None and isinstance(attribute, _FLOAT4_ATTRIBUTE):
        return attribute
    raise NamedAttributeError(
        f"Attribute '{attribute.name}' has an unsupported data type: "
        f"{attribute.data_type}"
    )


def list_attributes(
    obj: Object, evaluate: bool = False, drop_hidden: bool = False
) -> list[str]:
    """
    List the names of the attributes on an object, sorted alphabetically.

    Parameters
    ----------
    obj : bpy.types.Object
        The Blender object, with mesh, curves or point cloud data.
    evaluate : bool, optional
        Whether to list the attributes after evaluating modifiers, by default False.
    drop_hidden : bool, optional
        Whether to leave out hidden attributes, whose names start with `.`, by
        default False.

    Returns
    -------
    list[str]
        The attribute names.

    Raises
    ------
    TypeError
        If the object's data isn't a mesh, curves or point cloud.
    """
    if evaluate:
        strings = list(_attribute_data(evaluate_object(obj)).attributes.keys())
    else:
        strings = list(_attribute_data(obj).attributes.keys())

    # return a sorted list of attribute names because there is inconsistency
    # between blender versions for the order of attributes being iterated over
    strings.sort()

    if not drop_hidden:
        return strings

    return [x for x in strings if not x.startswith(".")]


class AttributeMismatchError(NamedAttributeError):
    """
    Exception raised when data doesn't fit an attribute.

    Raised when the number of values written with `Attribute.from_array` doesn't
    match the attribute, or when values can't be represented by the attribute's type
    (complex numbers, or integers outside the range of the storage type).
    """


class AttributeDomains(Enum):
    """
    Enumeration of attribute domains in Blender.

    Every attribute is stored on a domain, and has one value per element of that
    domain. An attribute can only be stored on a domain the geometry has.

    [More Info](https://docs.blender.org/api/current/bpy_types_enum_items/attribute_domain_items.html#rna-enum-attribute-domain-items)

    Attributes
    ----------
    POINT : str
        The point domain of geometry data which includes vertices, point cloud and control points of curves.
    EDGE : str
        The edges of meshes, defined as pairs of vertices.
    FACE : str
        The face domain of meshes, defined as groups of edges.
    CORNER : str
        The face corners of meshes, one for each vertex of each face.
    CURVE : str
        The Spline domain, which includes the individual splines that each contain at least one control point.
    INSTANCE : str
        The Instance domain, which can include sets of other geometry to be treated as a single group.
    LAYER : str
        The domain of single Grease Pencil layers.
    """

    POINT = "POINT"
    EDGE = "EDGE"
    FACE = "FACE"
    CORNER = "CORNER"
    CURVE = "CURVE"
    INSTANCE = "INSTANCE"
    LAYER = "LAYER"


ValueNames = Literal["value", "vector", "color", "color_srgb"]


@dataclass(frozen=True)
class AttributeType:
    """
    How databpy reads and writes one Blender attribute type.

    Attributes
    ----------
    type_name : str
        The Blender data type name, e.g. 'FLOAT_VECTOR'.
    value_name : str
        The property of each attribute value that is read and written, e.g. 'vector'.
    dtype : type
        The numpy dtype that values are stored in.
    dimensions : tuple[int, ...]
        The shape of a single value, e.g. (3,) or (4, 4).
    """

    type_name: AttributeTypeNames
    value_name: ValueNames
    dtype: type
    dimensions: tuple[int, ...]

    def __str__(self) -> str:
        return self.type_name


class AttributeTypes(Enum):
    """
    Enumeration of attribute types in Blender.

    Each attribute type has a specific data type and dimensionality that corresponds
    to Blender's internal CustomData types. The dtype values use explicit NumPy types
    (e.g., np.float32, np.uint8) that match Blender's internal storage precision.

    Notes
    -----
    All float types use np.float32 (not Python's float or np.float64) as this matches
    Blender's internal 32-bit float storage. BYTE_COLOR uses np.uint8 (unsigned) as it
    corresponds to Blender's MLoopCol struct which stores color components as unsigned
    char values (0-255 range).

    Attributes
    ----------
    FLOAT : AttributeType
        Single float value with dimensions (1,). Dtype: np.float32
        [More Info](https://docs.blender.org/api/current/bpy.types.FloatAttribute.html#bpy.types.FloatAttribute)
    FLOAT_VECTOR : AttributeType
        3D vector of floats with dimensions (3,). Dtype: np.float32
        [More Info](https://docs.blender.org/api/current/bpy.types.FloatVectorAttribute.html#bpy.types.FloatVectorAttribute)
    FLOAT2 : AttributeType
        2D vector of floats with dimensions (2,). Dtype: np.float32
        [More Info](https://docs.blender.org/api/current/bpy.types.Float2Attribute.html#bpy.types.Float2Attribute)
    FLOAT4 : AttributeType
        4D vector of floats with dimensions (4,). Dtype: np.float32. Requires
        Blender 5.2 or later, see `HAS_FLOAT4`.
        [More Info](https://docs.blender.org/api/current/bpy.types.Float4Attribute.html#bpy.types.Float4Attribute)
    FLOAT_COLOR : AttributeType
        RGBA color values as floats with dimensions (4,). Dtype: np.float32
        [More Info](https://docs.blender.org/api/current/bpy.types.FloatColorAttributeValue.html#bpy.types.FloatColorAttributeValue)
    BYTE_COLOR : AttributeType
        RGBA color values as unsigned 8-bit integers with dimensions (4,). Dtype: np.uint8
        [More Info](https://docs.blender.org/api/current/bpy.types.ByteColorAttribute.html#bpy.types.ByteColorAttribute)
    QUATERNION : AttributeType
        Quaternion rotation (w, x, y, z) as floats with dimensions (4,). Dtype: np.float32
        [More Info](https://docs.blender.org/api/current/bpy.types.QuaternionAttribute.html#bpy.types.QuaternionAttribute)
    INT : AttributeType
        Single 32-bit integer value with dimensions (1,). Dtype: np.int32
        [More Info](https://docs.blender.org/api/current/bpy.types.IntAttribute.html#bpy.types.IntAttribute)
    INT8 : AttributeType
        8-bit signed integer value with dimensions (1,). Dtype: np.int8
        [More Info](https://docs.blender.org/api/current/bpy.types.ByteIntAttributeValue.html#bpy.types.ByteIntAttributeValue)
    INT16_2D : AttributeType
        2D vector of 16-bit signed integers with dimensions (2,). Dtype: np.int16
        [More Info](https://docs.blender.org/api/current/bpy.types.Short2Attribute.html#bpy.types.Short2Attribute)
    INT32_2D : AttributeType
        2D vector of 32-bit integers with dimensions (2,). Dtype: np.int32
        [More Info](https://docs.blender.org/api/current/bpy.types.Int2Attribute.html#bpy.types.Int2Attribute)
    FLOAT4X4 : AttributeType
        4x4 transformation matrix of floats with dimensions (4, 4). Dtype: np.float32
        [More Info](https://docs.blender.org/api/current/bpy.types.Float4x4Attribute.html#bpy.types.Float4x4Attribute)
    BOOLEAN : AttributeType
        Single boolean value with dimensions (1,). Dtype: bool
        [More Info](https://docs.blender.org/api/current/bpy.types.BoolAttribute.html#bpy.types.BoolAttribute)
    STRING : AttributeType
        Text string value with dimensions (1,). Dtype: np.str_. Stored by Blender as
        bytes, and read and written one value at a time as `foreach_get` and
        `foreach_set` don't support string properties. Experimental: string attributes
        aren't yet properly supported within Geometry Nodes, so reading or writing them
        emits a warning.
        [More Info](https://docs.blender.org/api/current/bpy.types.StringAttribute.html#bpy.types.StringAttribute)
    """

    # CD_PROP_FLOAT (10): stored as float (MFloatProperty.f)
    FLOAT = AttributeType(
        type_name="FLOAT", value_name="value", dtype=np.float32, dimensions=(1,)
    )
    # CD_PROP_FLOAT3 (48): stored as float[3] (blender::float3)
    FLOAT_VECTOR = AttributeType(
        type_name="FLOAT_VECTOR", value_name="vector", dtype=np.float32, dimensions=(3,)
    )
    # CD_PROP_FLOAT2 (49): stored as float[2] (blender::float2)
    FLOAT2 = AttributeType(
        type_name="FLOAT2", value_name="vector", dtype=np.float32, dimensions=(2,)
    )
    # CD_PROP_FLOAT4: stored as float[4] (blender::float4)
    FLOAT4 = AttributeType(
        type_name="FLOAT4", value_name="vector", dtype=np.float32, dimensions=(4,)
    )
    # CD_PROP_COLOR (47): stored as float[4] (MPropCol.color, ColorGeometry4f = ColorSceneLinear4f<Premultiplied>)
    # alternatively use color_srgb to get the color info in sRGB color space, otherwise linear color space
    FLOAT_COLOR = AttributeType(
        type_name="FLOAT_COLOR", value_name="color", dtype=np.float32, dimensions=(4,)
    )
    # CD_PROP_BYTE_COLOR (17): stored as unsigned char r,g,b,a (MLoopCol, ColorGeometry4b = ColorSceneLinearByteEncoded4b<Premultiplied>)
    # the bytes are only exposed as floats, where `color_srgb` is the byte value / 255
    BYTE_COLOR = AttributeType(
        type_name="BYTE_COLOR",
        value_name="color_srgb",
        dtype=np.uint8,
        dimensions=(4,),
    )
    # CD_PROP_QUATERNION (52): stored as float[4] (blender::float4, blender::Quaternion)
    QUATERNION = AttributeType(
        type_name="QUATERNION", value_name="value", dtype=np.float32, dimensions=(4,)
    )
    # CD_PROP_INT32 (11): stored as int (MIntProperty.i)
    INT = AttributeType(
        type_name="INT", value_name="value", dtype=np.int32, dimensions=(1,)
    )
    # CD_PROP_INT8 (45): stored as int8_t (MInt8Property.i)
    INT8 = AttributeType(
        type_name="INT8", value_name="value", dtype=np.int8, dimensions=(1,)
    )
    # CD_PROP_INT16_2D: stored as int16_t[2] (blender::short2 = VecBase<int16_t, 2>)
    INT16_2D = AttributeType(
        type_name="INT16_2D", value_name="value", dtype=np.int16, dimensions=(2,)
    )
    # CD_PROP_INT32_2D (46): stored as int32_t[2] (blender::int2 = VecBase<int32_t, 2>)
    INT32_2D = AttributeType(
        type_name="INT32_2D", value_name="value", dtype=np.int32, dimensions=(2,)
    )
    # CD_PROP_FLOAT4X4 (20): stored as float[4][4] (blender::float4x4 = MatBase<float, 4, 4>)
    FLOAT4X4 = AttributeType(
        type_name="FLOAT4X4", value_name="value", dtype=np.float32, dimensions=(4, 4)
    )
    # CD_PROP_BOOL (50): stored as bool (MBoolProperty.b as uint8_t)
    BOOLEAN = AttributeType(
        type_name="BOOLEAN", value_name="value", dtype=bool, dimensions=(1,)
    )
    # CD_PROP_STRING (12): stored as MStringProperty (byte string)
    STRING = AttributeType(
        type_name="STRING", value_name="value", dtype=np.str_, dimensions=(1,)
    )


def guess_atype_from_array(array: np.ndarray) -> AttributeTypes:
    """
    Infer the attribute type for an array from its shape and dtype.

    - `(n,)` or `(n, 1)`: bool to BOOLEAN, int8 to INT8, other integers to INT,
      floats to FLOAT, and strings to STRING. Unsigned integers map to INT, as their
      values may not fit INT8.
    - `(n, 2)`: int16 to INT16_2D, other integers to INT32_2D, and floats to FLOAT2.
    - `(n, 3)`: any numeric dtype to FLOAT_VECTOR.
    - `(n, 4)`: uint8 to BYTE_COLOR, and other numeric dtypes to FLOAT4. Before
      Blender 5.2, which has no FLOAT4, they map to FLOAT_COLOR.
    - `(n, 4, 4)`: any numeric dtype to FLOAT4X4.

    FLOAT_COLOR and QUATERNION are never inferred, and must be passed as `atype`.

    Parameters
    ----------
    array : np.ndarray
        Input numpy array to analyze.

    Returns
    -------
    AttributeTypes
        The inferred attribute type enum value.

    Raises
    ------
    TypeError
        If input is not a numpy array.
    ValueError
        If the array has no dimensions, or no attribute type matches its shape and
        dtype.

    Examples
    --------
    >>> print(guess_atype_from_array(np.array([1.0, 2.0, 3.0], dtype=np.float32)))
    AttributeTypes.FLOAT
    >>> print(guess_atype_from_array(np.array([[1, 2], [3, 4]], dtype=np.int32)))
    AttributeTypes.INT32_2D
    >>> print(guess_atype_from_array(np.array([[255, 0, 0, 255]], dtype=np.uint8)))
    AttributeTypes.BYTE_COLOR
    """

    if not isinstance(array, np.ndarray):
        raise TypeError(f"`array` must be a numpy array, not {type(array)=}")
    if array.ndim == 0:
        raise ValueError(
            "`array` must have at least one dimension, with one row per element"
        )

    dtype = array.dtype
    kind = dtype.kind
    shape = array.shape
    n_row = shape[0]
    numeric = kind in "biuf"

    # Handle 1D arrays (single values per element)
    if shape == (n_row, 1) or shape == (n_row,):
        if kind == "b":
            return AttributeTypes.BOOLEAN
        elif kind == "i":
            return AttributeTypes.INT8 if dtype == np.int8 else AttributeTypes.INT
        elif kind == "u":
            # unsigned values (e.g. uint8 above 127) don't fit in the signed INT8
            return AttributeTypes.INT
        elif kind == "f":
            return AttributeTypes.FLOAT
        # String arrays (unicode, bytes or numpy 2.x StringDType)
        elif kind in ("U", "S", "T"):
            return AttributeTypes.STRING

    # Handle 2D arrays (vectors, colors, matrices)
    elif shape == (n_row, 2):
        if kind == "i":
            if dtype == np.int16:
                return AttributeTypes.INT16_2D
            return AttributeTypes.INT32_2D
        elif kind == "u":
            return AttributeTypes.INT32_2D
        elif kind == "f":
            return AttributeTypes.FLOAT2

    elif shape == (n_row, 3) and numeric:
        return AttributeTypes.FLOAT_VECTOR

    elif shape == (n_row, 4) and numeric:
        # 4D data - uint8 maps to BYTE_COLOR, everything else to the generic FLOAT4.
        # The color and quaternion types must be explicitly requested via `atype`
        if dtype == np.uint8:
            return AttributeTypes.BYTE_COLOR
        # before Blender 5.2 there is no generic FLOAT4, so fall back to FLOAT_COLOR
        return AttributeTypes.FLOAT4 if HAS_FLOAT4 else AttributeTypes.FLOAT_COLOR

    # Handle 3D arrays (matrices)
    elif shape == (n_row, 4, 4) and numeric:
        return AttributeTypes.FLOAT4X4

    raise ValueError(
        f"Unable to infer an attribute type for an array with shape {shape} and dtype "
        f"{dtype}. Pass `atype` explicitly or convert the data to a supported shape."
    )


def _trigger_data_update(obj_data) -> None:
    # tag the data-block so the depsgraph re-evaluates modifiers and the viewport redraws
    obj_data.update_tag()


def _as_storage_array(data: np.ndarray, atype: AttributeTypes) -> np.ndarray:
    """
    Flatten and cast data to the attribute's storage dtype.

    Casting to the storage dtype lets `foreach_set` use the fast buffer protocol path.
    Values that can't be represented in an integer storage type raise instead of
    silently wrapping around.
    """
    target = np.dtype(atype.value.dtype)
    source = data.dtype

    if source.kind == "c":
        raise AttributeMismatchError(
            f"Complex data cannot be stored in a `{atype.value.type_name}` attribute."
        )

    if (
        target.kind in "iu"
        and source.kind in "iuf"
        and data.size
        and not np.can_cast(source, target)
    ):
        info = np.iinfo(cast(np.dtype[np.integer], target))
        low, high = np.min(data), np.max(data)
        if (
            (source.kind == "f" and not (np.isfinite(low) and np.isfinite(high)))
            or low < info.min
            or high > info.max
        ):
            raise AttributeMismatchError(
                f"Values in the range [{low}, {high}] can't be stored in the `{atype.value.type_name}` "
                f"attribute, which stores {target} values in the range "
                f"[{info.min}, {info.max}]."
            )

    return np.ravel(data).astype(target, copy=False)


def _read_values(
    attribute: PossibleAttributeTypes, atype: AttributeTypes
) -> np.ndarray:
    """Read the values of a numeric attribute as a flat array of its storage dtype."""
    info = atype.value
    size = len(attribute.data) * math.prod(info.dimensions)
    if atype == AttributeTypes.BYTE_COLOR:
        # the bytes are only exposed as floats in [0, 1], which are read with a
        # float32 buffer as anything else is converted one value at a time
        values = np.empty(size, dtype=np.float32)
        attribute.data.foreach_get(info.value_name, values)
        return np.rint(values * 255).astype(np.uint8)
    values = np.empty(size, dtype=info.dtype)
    attribute.data.foreach_get(info.value_name, values)
    return values


def _write_values(
    attribute: PossibleAttributeTypes, atype: AttributeTypes, values: np.ndarray
) -> None:
    """Write a flat array from `_as_storage_array` to a numeric attribute."""
    if atype == AttributeTypes.BYTE_COLOR:
        values = values / np.float32(255)
    attribute.data.foreach_set(atype.value.value_name, values)


def _attribute_memory(
    attribute: PossibleAttributeTypes, atype: AttributeTypes
) -> np.ndarray | None:
    """A writable view of a numeric attribute's values in Blender's own memory.

    The values are laid out exactly as databpy reads them (BYTE_COLOR as raw bytes), so
    a few values can be written without transferring the whole attribute. Returns None
    where the values aren't stored as one contiguous array, e.g. a `SINGLE` value for
    the whole domain.

    The view is only valid until the geometry changes, as Blender can reallocate the
    values (e.g. when adding vertices), so it must be used immediately and discarded.
    """
    if atype == AttributeTypes.STRING or attribute.storage_type != "ARRAY":
        return None
    data = attribute.data
    n = len(data)
    if n == 0:
        return None
    info = atype.value
    item_size = np.dtype(info.dtype).itemsize * math.prod(info.dimensions)
    # accessing the values through RNA gives a pointer to memory that isn't shared
    # with other data-blocks, so writes only affect this attribute
    start = data[0].as_pointer()
    if start == 0 or data[n - 1].as_pointer() - start != (n - 1) * item_size:
        return None
    buffer = (ctypes.c_char * (n * item_size)).from_address(start)
    values = np.frombuffer(buffer, dtype=info.dtype)
    return values if info.dimensions == (1,) else values.reshape(n, *info.dimensions)


def _warn_string_support() -> None:
    # STRING attributes are accessible through the Python API but aren't yet properly
    # supported in Geometry Nodes, so treat their use as experimental for now. The
    # warning points at the first frame outside databpy, so Python's default filter
    # shows it once per call site
    warnings.warn(
        "String attributes can be read and written through the Python API but are not "
        "yet properly supported within Geometry Nodes. Support may change in future "
        "Blender / databpy versions.",
        skip_file_prefixes=(os.path.dirname(__file__),),
    )


def _as_string_attribute(attribute: bpy.types.Attribute) -> bpy.types.StringAttribute:
    if not isinstance(attribute, bpy.types.StringAttribute):
        raise NamedAttributeError(
            f"Attribute '{attribute.name}' is of type '{attribute.data_type}', "
            "expected a STRING attribute"
        )
    return attribute


def _read_string_values(attribute: bpy.types.Attribute) -> np.ndarray:
    # STRING attributes don't support `foreach_get` so values are read individually.
    # Blender stores byte strings, which are decoded to a unicode string array
    _warn_string_support()
    return np.array(
        [item.value.decode("utf-8") for item in _as_string_attribute(attribute).data]
    )


def _write_string_values(attribute: bpy.types.Attribute, array: np.ndarray) -> None:
    # STRING attributes don't support `foreach_set` so values are set individually.
    # Blender only accepts bytes, so unicode values are encoded first
    _warn_string_support()
    for item, value in zip(_as_string_attribute(attribute).data, np.ravel(array)):
        item.value = value.encode("utf-8") if isinstance(value, str) else bytes(value)


class Attribute:
    """
    Low-level wrapper around a Blender attribute with explicit reads and writes.

    Values are only read by `as_array` and only written by `from_array`. Use this
    class to control when values are transferred, for example to apply several
    whole-array operations with a single write, or to inspect an attribute's type,
    domain and shape without reading its values.

    For automatic syncing, use `AttributeArray`, a numpy array subclass that writes
    changes back to Blender as they are made.

    Architecture
    ------------
    - `Attribute`: Low-level, manual control (this class)
    - `AttributeArray`: High-level, automatically syncing numpy subclass
    - `BlenderObject["attr"]`: Convenience accessor returning AttributeArray

    Parameters
    ----------
    attribute : bpy.types.Attribute
        The Blender attribute to wrap.

    Raises
    ------
    NamedAttributeError
        If the attribute has an unsupported data type.

    Attributes
    ----------
    attribute : bpy.types.Attribute
        The underlying Blender attribute.
    name : str
        Name of the attribute.
    atype : AttributeTypes
        Enum value representing the attribute's data type.
    domain : AttributeDomains
        Enum value representing the attribute's domain (POINT, EDGE, FACE, etc.).
    shape : tuple
        Full shape including number of elements and component dimensions.
    dtype : Type
        NumPy dtype corresponding to the attribute type.

    Examples
    --------
    Manual read/write workflow:

    ```python
    import databpy as db
    import numpy as np

    obj = db.create_object(np.random.rand(10, 3))
    attr = db.Attribute(obj.data.attributes["position"])

    # Read once
    positions = attr.as_array()
    positions[:, 2] += 1.0

    # Write once
    attr.from_array(positions)
    ```

    Compare with AttributeArray, which writes each change as it is made:

    ```python
    import databpy as db
    import numpy as np

    bob = db.create_bob(np.random.rand(10, 3))
    bob.position[:, 2] += 1.0  # writes the new z values immediately
    ```

    See Also
    --------
    AttributeArray : Automatically syncing numpy subclass
    store_named_attribute : Create or update attributes
    named_attribute : Convenience function to read attribute data
    """

    def __init__(self, attribute: bpy.types.Attribute):
        self.attribute: PossibleAttributeTypes = _as_typed_attribute(attribute)

    def __len__(self) -> int:
        """
        Returns the number of attribute elements.

        Returns
        -------
        int
            The number of elements in the attribute.
        """
        return len(self.attribute.data)

    @property
    def name(self) -> str:
        """
        Returns the name of the attribute.

        Returns
        -------
        str
            The name of the attribute.
        """
        return self.attribute.name

    @property
    def atype(self) -> AttributeTypes:
        """
        Returns the attribute type information for this attribute.

        Returns
        -------
        AttributeTypes
            The enum member representing the attribute's data type.
        """
        return AttributeTypes[self.attribute.data_type]

    @property
    def domain(self) -> AttributeDomains:
        """
        Returns the attribute domain for this attribute.

        Returns
        -------
        AttributeDomains
            The enum member representing the attribute's domain.
        """
        return AttributeDomains[self.attribute.domain]

    @property
    def value_name(self) -> ValueNames:
        """Returns the Blender property name for accessing values (e.g., 'value', 'vector', 'color')."""
        return self.atype.value.value_name

    @property
    def is_1d(self) -> bool:
        """Returns True if the attribute stores single scalar values per element."""
        return self.atype.value.dimensions == (1,)

    @property
    def type_name(self) -> AttributeTypeNames:
        """Returns the Blender attribute type name (e.g., 'FLOAT_VECTOR', 'INT', 'BOOLEAN')."""
        return self.atype.value.type_name

    @property
    def storage_type(self) -> StorageTypeNames:
        """
        Returns how Blender stores the attribute internally.

        'ARRAY' is a full array of values, while 'SINGLE' is a single value for the
        entire domain (which can appear on evaluated geometry from Geometry Nodes).
        Reading works the same either way, as `data` has one item per element.
        """
        return self.attribute.storage_type

    @property
    def shape(self) -> tuple[int, ...]:
        """Returns the full shape of the attribute array including element dimensions."""
        return (len(self), *self.atype.value.dimensions)

    @property
    def dtype(self) -> type:
        """Returns the numpy dtype for this attribute type."""
        return self.atype.value.dtype

    @property
    def n_values(self) -> int:
        """Returns the total number of scalar values in the attribute.

        Deprecated: use `size` instead, as this will be removed in databpy 0.13.0.
        """
        warnings.warn(
            "`Attribute.n_values` is deprecated in favour of `Attribute.size` and will be "
            f"removed in databpy {REMOVAL_VERSION}.",
            FutureWarning,
            stacklevel=2,
        )
        return self.size

    @property
    def size(self) -> int:
        """Returns the total number of scalar values in the attribute."""
        return math.prod(self.shape)

    def from_array(self, array: npt.ArrayLike) -> None:
        """
        Write the values of an array to the attribute.

        The array can have any shape with the same number of values as the attribute,
        such as a flat array, and is read in C order. Values are cast to the
        attribute's storage dtype.

        Parameters
        ----------
        array : npt.ArrayLike
            The values to write, as a numpy array or anything convertible to one.

        Raises
        ------
        AttributeMismatchError
            If the number of values doesn't match the attribute's `size`, or the
            values can't be represented by the attribute's type.
        """
        array = np.asarray(array)
        if array.size != self.size:
            raise AttributeMismatchError(
                f"Array size {array.size} does not match attribute size {self.size}. "
                f"Array shape {array.shape} cannot be reshaped to attribute shape {self.shape}"
            )

        if self.atype == AttributeTypes.STRING:
            _write_string_values(self.attribute, array)
        else:
            _write_values(
                self.attribute, self.atype, _as_storage_array(array, self.atype)
            )

        _trigger_data_update(self.attribute.id_data)

    def as_array(self) -> np.ndarray:
        """
        Read the attribute's values into a new numpy array.

        Returns
        -------
        np.ndarray
            The values, with the attribute's `shape` and `dtype`. BYTE_COLOR values
            are uint8 from 0 to 255.
        """

        atype = self.atype
        if atype == AttributeTypes.STRING:
            return _read_string_values(self.attribute)

        array = _read_values(self.attribute, atype)

        # if the attribute has more than one dimension reshape the array before returning
        if atype.value.dimensions == (1,):
            return array
        return array.reshape(-1, *atype.value.dimensions)

    def __str__(self) -> str:
        return f"Attribute: {self.attribute.name}, type: {self.type_name}, size: {self.shape}"


def _match_atype(
    atype: AttributeTypeNames | AttributeTypes | None, data: np.ndarray
) -> AttributeTypes:
    if isinstance(atype, str):
        try:
            atype = AttributeTypes[atype]
        except KeyError:
            raise ValueError(
                f"Given data type {atype=} does not match any of the possible attribute types: {list(AttributeTypes)=}"
            )
    if atype is None:
        atype = guess_atype_from_array(data)
    if atype is AttributeTypes.FLOAT4 and not HAS_FLOAT4:
        raise ValueError(
            "The FLOAT4 attribute type requires Blender 5.2 or later. Use FLOAT_COLOR "
            "or QUATERNION to store 4D data in earlier versions."
        )
    return atype


def _match_domain(domain: DomainNames | AttributeDomains) -> DomainNames:
    if isinstance(domain, AttributeDomains):
        return domain.value
    try:
        AttributeDomains[domain]  # Validate the string is a valid domain
    except KeyError:
        raise ValueError(
            f"Given domain {domain=} does not match any of the possible attribute domains: {list(AttributeDomains)=}"
        )
    return domain


def store_named_attribute(
    obj: bpy.types.Object,
    data: npt.ArrayLike,
    name: str,
    atype: AttributeTypeNames | AttributeTypes | None = None,
    domain: DomainNames | AttributeDomains | None = None,
    overwrite: bool = True,
) -> bpy.types.Attribute:
    """
    Write values to a named attribute on the object, creating it if needed.

    Parameters
    ----------
    obj : bpy.types.Object
        The Blender object, with mesh, curves or point cloud data.
    data : npt.ArrayLike
        The attribute data, as a numpy array or anything convertible to one.
    name : str
        The name of the attribute.
    atype : str or AttributeTypes or None, optional
        The attribute type to store the data as. If None, the type of an existing
        attribute is used, otherwise the type is inferred from data.
    domain : str or AttributeDomains or None, optional
        The domain of the attribute. If None, the domain of an existing attribute is
        used, otherwise 'POINT'.
    overwrite : bool, optional
        Whether to write to an existing attribute with the same name, by default
        True. If False, a new attribute is created, which Blender gives a unique name
        such as `name.001`.

    Returns
    -------
    bpy.types.Attribute
        The created or modified attribute.

    Raises
    ------
    ValueError
        If atype or domain doesn't match an available type or domain, no type can be
        inferred, or atype is FLOAT4 before Blender 5.2.
    NamedAttributeError
        If the object doesn't hold attributes, the name is empty, the data size
        doesn't match the domain, the atype or domain conflict with an existing
        attribute, or the attribute can't be created on the domain.
    AttributeMismatchError
        If the values can't be represented by the attribute's type.

    Examples
    --------
    ```{python}
    import bpy
    import numpy as np
    from databpy import store_named_attribute, list_attributes, named_attribute
    obj = bpy.data.objects["Cube"]
    print(f"{list_attributes(obj)=}")
    ```
    ```{python}
    store_named_attribute(obj, np.arange(8), "test_attribute")
    print(f"{list_attributes(obj)=}")
    ```
    ```{python}
    named_attribute(obj, "test_attribute")
    ```
    """

    data = np.asarray(data)
    obj_data = obj.data

    if not isinstance(
        obj_data, (bpy.types.Mesh, bpy.types.Curves, bpy.types.PointCloud)
    ):
        raise NamedAttributeError(
            f"Object must be a mesh, curve or point cloud to store attributes, not {type(obj_data)}"
        )

    if name == "":
        raise NamedAttributeError("Attribute name cannot be an empty string.")

    existing_attribute = obj_data.attributes.get(name) if overwrite else None
    if existing_attribute is not None:
        # writing to an existing attribute keeps its type and domain
        attribute = _as_typed_attribute(existing_attribute)
        existing_atype = AttributeTypes[attribute.data_type]
        atype = existing_atype if atype is None else _match_atype(atype, data)
        if domain is not None and _match_domain(domain) != attribute.domain:
            raise NamedAttributeError(
                f"Attribute `{name}` already exists on the `{attribute.domain}` domain, "
                f"not `{_match_domain(domain)}`. Remove it first to store it on a "
                "different domain."
            )
        domain = attribute.domain
    else:
        atype = _match_atype(atype, data)
        domain = _match_domain(AttributeDomains.POINT if domain is None else domain)
        current_names = obj_data.attributes.keys()
        try:
            new_attribute = obj_data.attributes.new(name, atype.value.type_name, domain)
        except RuntimeError:
            # e.g. a domain that isn't supported by this geometry type
            new_attribute = None

        if new_attribute is None:
            # remove any attributes that were created as part of the failed attempt
            added_names = [
                added.name
                for added in obj_data.attributes
                if added.name not in current_names
            ]
            for attr_name in added_names:
                obj_data.attributes.remove(obj_data.attributes[attr_name])
            raise NamedAttributeError(
                f"Could not create attribute `{name}` of type `{atype.value.type_name}` on domain `{domain}`. "
                "Potentially the attribute name is too long or there is no geometry on the object for the given domain."
            )
        attribute = _as_typed_attribute(new_attribute)

    target_atype = AttributeTypes[attribute.data_type]

    # Calculate expected shape for the attribute
    expected_shape = (len(attribute.data), *target_atype.value.dimensions)

    # Check if we need to reshape the data
    if data.shape != expected_shape:
        # Check if total number of elements matches
        expected_size = np.prod(expected_shape)
        if data.size != expected_size:
            raise NamedAttributeError(
                f"Data size {data.size} (shape {data.shape}) does not match the required size {expected_size} "
                f"for domain `{domain}` with {len(attribute.data)} elements and dimensions {target_atype.value.dimensions}"
            )

        # Try to reshape the data
        try:
            data = data.reshape(expected_shape)
        except ValueError as e:
            raise NamedAttributeError(
                f"Data shape {data.shape} cannot be reshaped to expected shape {expected_shape}: {e}"
            )

    if target_atype != atype:
        raise NamedAttributeError(
            f"Attribute being written to: `{attribute.name}` of type `{target_atype.value.type_name}` does not match the type for the given data: `{atype.value.type_name}`"
        )

    if atype == AttributeTypes.STRING:
        _write_string_values(attribute, data)
    else:
        # the 'foreach_set' requires a 1D array, regardless of the shape of the attribute
        _write_values(attribute, atype, _as_storage_array(data, atype))

    _trigger_data_update(obj_data)

    return attribute


def evaluate_object(
    obj: bpy.types.Object, context: bpy.types.Context | None = None
) -> bpy.types.Object:
    """
    Return the object with its modifiers evaluated.

    Parameters
    ----------
    obj : bpy.types.Object
        The Blender object to evaluate.
    context : bpy.types.Context | None, optional
        The Blender context to use for evaluation, by default None

    Returns
    -------
    bpy.types.Object
        The evaluated object with modifiers applied.

    Raises
    ------
    TypeError
        If `obj` isn't an object, or its data isn't a mesh, curves or point cloud.

    Notes
    -----
    The object is tagged for an update, then read from the evaluated depsgraph of
    `context`, or of `bpy.context` if no context is given.

    Examples
    --------
    ```{python}
    import bpy
    from databpy import evaluate_object
    obj = bpy.data.objects['Cube']
    evaluated_obj = evaluate_object(obj)
    ```
    """
    if context is None:
        context = bpy.context
    _check_obj_attributes(obj)
    obj.update_tag()
    return obj.evaluated_get(context.evaluated_depsgraph_get())


def named_attribute(
    obj: bpy.types.Object, name: str = "position", evaluate: bool = False
) -> np.ndarray:
    """
    Read the values of a named attribute into a numpy array.

    Parameters
    ----------
    obj : bpy.types.Object
        The Blender object.
    name : str, optional
        The name of the attribute, by default 'position'.
    evaluate : bool, optional
        Whether to evaluate modifiers before reading, by default False.

    Returns
    -------
    np.ndarray
        The attribute data as a numpy array.

    Raises
    ------
    AttributeNotFoundError
        If the named attribute does not exist on the object.
    TypeError
        If `obj` isn't an object, or its data isn't a mesh, curves or point cloud.

    Examples
    --------
    ```{python}
    import bpy
    from databpy import named_attribute, list_attributes
    obj = bpy.data.objects["Cube"]
    print(f"{list_attributes(obj)=}")
    ```
    ```{python}
    named_attribute(obj, "position")
    ```

    """
    _check_obj_attributes(obj)

    if evaluate:
        obj = evaluate_object(obj)

    try:
        attr = Attribute(_attribute_data(obj).attributes[name])
    except KeyError:
        raise AttributeNotFoundError(
            f"The selected attribute '{name}' does not exist on the object. "
            f"Available attributes: {list_attributes(obj, evaluate=evaluate)}"
        ) from None

    return attr.as_array()


def remove_named_attribute(obj: bpy.types.Object, name: str) -> None:
    """
    Remove a named attribute from an object.

    Parameters
    ----------
    obj : bpy.types.Object
        The Blender object.
    name : str
        Name of the attribute to remove.

    Raises
    ------
    AttributeNotFoundError
        If the named attribute does not exist on the object.
    TypeError
        If `obj` isn't an object, or its data isn't a mesh, curves or point cloud.
    NamedAttributeError
        If the attribute is required by Blender (e.g. `position`) and can't be removed.

    Examples
    --------
    ```{python}
    import bpy
    import numpy as np
    from databpy import remove_named_attribute, list_attributes, store_named_attribute
    obj = bpy.data.objects["Cube"]
    store_named_attribute(obj, np.random.rand(8, 3), "random_numbers")
    print(f"{list_attributes(obj)=}")
    ```
    ```{python}
    remove_named_attribute(obj, "random_numbers")
    print(f"{list_attributes(obj)=}")
    ```
    """
    _check_obj_attributes(obj)
    obj_data = _attribute_data(obj)
    try:
        attr = obj_data.attributes[name]
    except KeyError:
        raise AttributeNotFoundError(
            f"The selected attribute '{name}' does not exist on the object"
        ) from None
    try:
        obj_data.attributes.remove(attr)
    except RuntimeError as e:
        raise NamedAttributeError(
            f"The attribute '{name}' is required by Blender and can't be removed"
        ) from e
