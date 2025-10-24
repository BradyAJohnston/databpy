from dataclasses import dataclass
from enum import Enum
from typing import Type
import bpy
from bpy.types import Object
import numpy as np
import warnings

COMPATIBLE_TYPES = [bpy.types.Mesh, bpy.types.Curves, bpy.types.PointCloud]


class NamedAttributeError(AttributeError):
    """
    Base exception for all attribute-related errors in databpy.

    This exception is raised when operations on Blender named attributes fail,
    such as when an attribute doesn't exist, has incorrect dimensions, or
    cannot be created.
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


def _check_obj_attributes(obj: Object) -> None:
    if not isinstance(obj, bpy.types.Object):
        raise TypeError(f"Object must be a bpy.types.Object, not {type(obj)}")
    if not any(isinstance(obj.data, obj_type) for obj_type in COMPATIBLE_TYPES):
        raise TypeError(
            f"The object is not a a compatible type.\n- Obj: {obj}\n- Compatitble Types: {COMPATIBLE_TYPES}"
        )


def _check_is_mesh(obj: Object) -> None:
    if not isinstance(obj.data, bpy.types.Mesh):
        raise TypeError("Object must be a mesh to evaluate the modifiers")


def list_attributes(
    obj: Object, evaluate: bool = False, drop_hidden: bool = False
) -> list[str]:
    if evaluate:
        strings = list(evaluate_object(obj).data.attributes.keys())
    else:
        strings = list(obj.data.attributes.keys())

    # return a sorted list of attribute names because there is inconsistency
    # between blender versions for the order of attributes being iterated over
    strings.sort()

    if not drop_hidden:
        return strings

    return [x for x in strings if not x.startswith(".")]


@dataclass
class AttributeTypeInfo:
    dname: str
    dtype: type
    width: int


@dataclass
class AttributeDomain:
    name: str

    def __str__(self):
        return self.name


class AttributeMismatchError(NamedAttributeError):
    """
    Exception raised when attribute data doesn't match expected dimensions or types.

    This is a specialized NamedAttributeError for situations where an attribute
    exists but the data being written doesn't match the attribute's expected
    shape, size, or type.
    """

    pass


class AttributeDomains(Enum):
    """
    Enumeration of attribute domains in Blender. You can store an attribute onto one of
    these domains if there is corressponding geometry. All data is on a domain on geometry.

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
        The face domain of meshes, defined as pairs of edges that share a vertex.
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


@dataclass
class AttributeType:
    type_name: str
    value_name: str
    dtype: Type
    dimensions: tuple

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
    INT32_2D : AttributeType
        2D vector of 32-bit integers with dimensions (2,). Dtype: np.int32
        [More Info](https://docs.blender.org/api/current/bpy.types.Int2Attribute.html#bpy.types.Int2Attribute)
    FLOAT4X4 : AttributeType
        4x4 transformation matrix of floats with dimensions (4, 4). Dtype: np.float32
        [More Info](https://docs.blender.org/api/current/bpy.types.Float4x4Attribute.html#bpy.types.Float4x4Attribute)
    BOOLEAN : AttributeType
        Single boolean value with dimensions (1,). Dtype: bool
        [More Info](https://docs.blender.org/api/current/bpy.types.BoolAttribute.html#bpy.types.BoolAttribute)
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
    # CD_PROP_COLOR (47): stored as float[4] (MPropCol.color, ColorGeometry4f = ColorSceneLinear4f<Premultiplied>)
    # alternatively use color_srgb to get the color info in sRGB color space, otherwise linear color space
    FLOAT_COLOR = AttributeType(
        type_name="FLOAT_COLOR", value_name="color", dtype=np.float32, dimensions=(4,)
    )
    # CD_PROP_BYTE_COLOR (17): stored as unsigned char r,g,b,a (MLoopCol, ColorGeometry4b = ColorSceneLinearByteEncoded4b<Premultiplied>)
    BYTE_COLOR = AttributeType(
        type_name="BYTE_COLOR", value_name="color", dtype=np.uint8, dimensions=(4,)
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


def guess_atype_from_array(array: np.ndarray) -> AttributeTypes:
    """
    Determine the appropriate AttributeType based on array shape and dtype.

    This function matches arrays broadly to Blender attribute types while ensuring
    they are categorized correctly based on both shape and dtype. It handles:
    - Integer types: distinguishes int8, int32, and int32_2d based on dtype and shape
    - Float types: all floating point arrays map to float32-based attributes
    - Color types: distinguishes BYTE_COLOR (uint8) from FLOAT_COLOR (float32)
    - Boolean types: maps bool arrays to BOOLEAN attributes

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
    ValueError
        If input is not a numpy array.

    Examples
    --------
    >>> guess_atype_from_array(np.array([1.0, 2.0, 3.0], dtype=np.float32))
    AttributeTypes.FLOAT
    >>> guess_atype_from_array(np.array([[1, 2], [3, 4]], dtype=np.int32))
    AttributeTypes.INT32_2D
    >>> guess_atype_from_array(np.array([[255, 0, 0, 255]], dtype=np.uint8))
    AttributeTypes.BYTE_COLOR
    """

    if not isinstance(array, np.ndarray):
        raise ValueError(f"`array` must be a numpy array, not {type(array)=}")

    dtype = array.dtype
    shape = array.shape
    n_row = shape[0]

    # Handle 1D arrays (single values per element)
    if shape == (n_row, 1) or shape == (n_row,):
        # Boolean arrays
        if np.issubdtype(dtype, np.bool_):
            return AttributeTypes.BOOLEAN
        # Integer arrays - check for int8 vs int32
        elif np.issubdtype(dtype, np.integer):
            # Check if it's int8 or uint8 (but not for colors)
            if dtype in (np.int8, np.uint8):
                return AttributeTypes.INT8
            else:
                # All other integer types default to INT (int32)
                return AttributeTypes.INT
        # Float arrays
        elif np.issubdtype(dtype, np.floating):
            return AttributeTypes.FLOAT

    # Handle 2D arrays (vectors, colors, matrices)
    elif shape == (n_row, 2):
        # 2D vectors - check dtype to determine int32_2d vs float2
        if np.issubdtype(dtype, np.integer):
            return AttributeTypes.INT32_2D
        elif np.issubdtype(dtype, np.floating):
            return AttributeTypes.FLOAT2

    elif shape == (n_row, 3):
        # 3D vectors (FLOAT_VECTOR expects float32)
        return AttributeTypes.FLOAT_VECTOR

    elif shape == (n_row, 4):
        # 4D data - distinguish between BYTE_COLOR and FLOAT_COLOR based on dtype
        if dtype == np.uint8:
            return AttributeTypes.BYTE_COLOR
        else:
            # All other types (float32, float64, int, etc.) default to FLOAT_COLOR
            return AttributeTypes.FLOAT_COLOR

    # Handle 3D arrays (matrices)
    elif shape == (n_row, 4, 4):
        return AttributeTypes.FLOAT4X4

    # Default fallback
    return AttributeTypes.FLOAT


class Attribute:
    """
    Low-level wrapper around a Blender attribute providing manual get/set operations.

    This class provides direct, stateless access to Blender attributes with explicit
    control over when data is read from or written to Blender. Use this when you need:
    - Fine-grained control over read/write timing
    - One-time read or write operations without auto-sync overhead
    - To work with attribute metadata (type, domain, shape)

    For interactive workflows with automatic syncing, use `AttributeArray` instead,
    which subclasses numpy.ndarray and automatically writes changes back to Blender.

    Architecture
    ------------
    - `Attribute`: Low-level, manual control (this class)
    - `AttributeArray`: High-level, auto-syncing numpy subclass
    - `BlenderObject["attr"]`: Convenience accessor returning AttributeArray

    Parameters
    ----------
    attribute : bpy.types.Attribute
        The Blender attribute to wrap.

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

    Compare with AttributeArray auto-sync:

    ```python
    import databpy as db

    bob = db.create_bob(np.random.rand(10, 3))
    # Each operation automatically syncs
    bob.position[:, 2] += 1.0  # Writes immediately
    ```

    See Also
    --------
    AttributeArray : Auto-syncing numpy subclass for interactive workflows
    store_named_attribute : Create or update attributes
    named_attribute : Convenience function to read attribute data
    """

    def __init__(self, attribute: bpy.types.Attribute):
        self.attribute = attribute

    def __len__(self):
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
        AttributeType
            The type information of the attribute.
        """
        return AttributeTypes[self.attribute.data_type]

    @property
    def domain(self) -> AttributeDomains:
        """
        Returns the attribute domain for this attribute.

        Returns
        -------
        AttributeDomain
            The domain of the attribute.
        """
        return AttributeDomains[self.attribute.domain]

    @property
    def value_name(self) -> str:
        """Returns the Blender property name for accessing values (e.g., 'value', 'vector', 'color')."""
        return self.atype.value.value_name

    @property
    def is_1d(self) -> bool:
        """Returns True if the attribute stores single scalar values per element."""
        return self.atype.value.dimensions == (1,)

    @property
    def type_name(self) -> str:
        """Returns the Blender attribute type name (e.g., 'FLOAT_VECTOR', 'INT', 'BOOLEAN')."""
        return self.atype.value.type_name

    @property
    def shape(self) -> tuple:
        """Returns the full shape of the attribute array including element dimensions."""
        return (len(self), *self.atype.value.dimensions)

    @property
    def dtype(self) -> Type:
        """Returns the numpy dtype for this attribute type."""
        return self.atype.value.dtype

    @property
    def n_values(self) -> int:
        """Returns the total number of scalar values in the attribute."""
        # TODO: remove in future version
        # added in 0.4.2
        warnings.warn(
            message="`self.n_values` has been deprecated in favor of `self.size` and will be removed in future versions.",
            category=DeprecationWarning,
        )
        return self.size

    @property
    def size(self) -> int:
        """Returns the total number of scalar values in the attribute."""
        return np.prod(self.shape, dtype=int)

    def from_array(self, array: np.ndarray) -> None:
        """
        Set the attribute data from a numpy array.

        If the array is 1D and can be reshaped to match the attribute shape,
        it will be automatically reshaped.

        Parameters
        ----------
        array : np.ndarray
            Array containing the data to set. Must have the same total number
            of elements as the attribute.

        Raises
        ------
        AttributeMismatchError
            If array cannot be reshaped to match attribute shape.
        """
        if array.size != self.size:
            raise AttributeMismatchError(
                f"Array size {array.size} does not match attribute size {self.size}. "
                f"Array shape {array.shape} cannot be reshaped to attribute shape {self.shape}"
            )

        self.attribute.data.foreach_set(self.value_name, np.ravel(array))

    def as_array(self) -> np.ndarray:
        """
        Returns the attribute data as a numpy array.

        Returns
        -------
        np.ndarray
            Array containing the attribute data with appropriate shape and dtype.
        """

        # initialize empty 1D array that is needed to then be filled with values
        # from the Blender attribute
        array = np.zeros(self.size, dtype=self.dtype)
        self.attribute.data.foreach_get(self.value_name, array)

        # if the attribute has more than one dimension reshape the array before returning
        if self.is_1d:
            return array
        else:
            return array.reshape(self.shape)

    def __str__(self):
        return "Attribute: {}, type: {}, size: {}".format(
            self.attribute.name, self.type_name, self.shape
        )


def _match_atype(
    atype: str | AttributeTypes | None, data: np.ndarray
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
    return atype


def _match_domain(
    domain: str | AttributeDomains | None,
) -> str:
    if isinstance(domain, str):
        try:
            AttributeDomains[domain]  # Validate the string is a valid domain
            return domain
        except KeyError:
            raise ValueError(
                f"Given domain {domain=} does not match any of the possible attribute domains: {list(AttributeDomains)=}"
            )
    if domain is None:
        return AttributeDomains.POINT.value
    if isinstance(domain, AttributeDomains):
        return domain.value
    return domain


def store_named_attribute(
    obj: bpy.types.Object,
    data: np.ndarray,
    name: str,
    atype: str | AttributeTypes | None = None,
    domain: str | AttributeDomains = AttributeDomains.POINT,
    overwrite: bool = True,
) -> bpy.types.Attribute:
    """
    Adds and sets the values of an attribute on the object.

    Parameters
    ----------
    obj : bpy.types.Object
        The Blender object.
    data : np.ndarray
        The attribute data as a numpy array.
    name : str
        The name of the attribute.
    atype : str or AttributeTypes or None, optional
        The attribute type to store the data as. If None, type is inferred from data.
    domain : str or AttributeDomains, optional
        The domain of the attribute, by default 'POINT'.
    overwrite : bool, optional
        Whether to overwrite existing attribute, by default True.

    Returns
    -------
    bpy.types.Attribute
        The added or modified attribute.

    Raises
    ------
    ValueError
        If atype string doesn't match available types.
    AttributeMismatchError
        If data length doesn't match domain size.

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

    atype = _match_atype(atype, data)
    domain = _match_domain(domain)

    if isinstance(obj, bpy.types.Object):
        obj_data = obj.data
    else:
        obj_data = obj.data

    if not isinstance(
        obj_data, (bpy.types.Mesh, bpy.types.Curves, bpy.types.PointCloud)
    ):
        raise NamedAttributeError(
            f"Object must be a mesh, curve or point cloud to store attributes, not {type(obj_data)}"
        )

    if name == "":
        raise NamedAttributeError("Attribute name cannot be an empty string.")

    attribute = obj_data.attributes.get(name)  # type: ignore
    if not attribute or not overwrite:
        current_names = obj_data.attributes.keys()
        attribute = obj_data.attributes.new(name, atype.value.type_name, domain)

        if attribute is None:
            [
                obj_data.attributes.remove(obj_data.attributes[name])
                for name in obj_data.attributes.keys()
                if name not in current_names
            ]  # type: ignore
            raise NamedAttributeError(
                f"Could not create attribute `{name}` of type `{atype.value.type_name}` on domain `{domain}`. "
                "Potentially the attribute name is too long or there is no geometry on the object for the given domain."
            )

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

    # the 'foreach_set' requires a 1D array, regardless of the shape of the attribute
    # so we have to flatten it first
    attribute.data.foreach_set(atype.value.value_name, np.ravel(data))

    # The updating of data doesn't work 100% of the time (see:
    # https://projects.blender.org/blender/blender/issues/118507) so this resetting of a
    # single vertex is the current fix. Not great as I can see it breaking when we are
    # missing a vertex - but for now we shouldn't be dealing with any situations where this
    # is the case For now we will set a single vert to it's own position, which triggers a
    # proper refresh of the object data.
    try:
        obj.data.vertices[0].co = obj.data.vertices[0].co  # type: ignore
    except AttributeError:
        obj.data.update()  # type: ignore

    return attribute


def evaluate_object(
    obj: bpy.types.Object, context: bpy.types.Context | None = None
) -> bpy.types.Object:
    """
    Return an object which has the modifiers evaluated.

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

    Notes
    -----
    This function evaluates the object's modifiers using the current depsgraph.
    If no context is provided, it uses the current bpy.context.

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
    _check_is_mesh(obj)
    obj.update_tag()
    return obj.evaluated_get(context.evaluated_depsgraph_get())


def named_attribute(
    obj: bpy.types.Object, name="position", evaluate=False
) -> np.ndarray:
    """
    Get the named attribute data from the object.

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
    AttributeError
        If the named attribute does not exist on the mesh.

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
        _check_is_mesh(obj)

        obj = evaluate_object(obj)

    verbose = False
    try:
        attr = Attribute(obj.data.attributes[name])
    except KeyError:
        message = f"The selected attribute '{name}' does not exist on the mesh."
        if verbose:
            message += f"Possible attributes are: {obj.data.attributes.keys()}"

        raise NamedAttributeError(message)

    return attr.as_array()


def remove_named_attribute(obj: bpy.types.Object, name: str):
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
    AttributeError
        If the named attribute does not exist on the mesh.

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
    try:
        attr = obj.data.attributes[name]
        obj.data.attributes.remove(attr)
    except KeyError:
        raise NamedAttributeError(
            f"The selected attribute '{name}' does not exist on the object"
        )
