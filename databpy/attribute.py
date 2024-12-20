from dataclasses import dataclass
from enum import Enum
from typing import Type
import bpy
from bpy.types import Mesh, PointCloud, Curve, Object
import numpy as np
from pathlib import Path

COMPATIBLE_TYPES = [bpy.types.Mesh, bpy.types.Curve, bpy.types.PointCloud]


class NamedAttributeError(AttributeError):
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
        raise TypeError(f"Object must be a mesh to evaluate the modifiers")


def path_resolve(path: str | Path) -> Path:
    """
    Resolve a path string or Path object to an absolute Path.

    Parameters
    ----------
    path : str or Path
        The path to resolve, either as a string or Path object.

    Returns
    -------
    Path
        The resolved absolute Path.

    Raises
    ------
    ValueError
        If the path cannot be resolved.
    """

    if isinstance(path, str):
        return Path(bpy.path.abspath(path))
    elif isinstance(path, Path):
        return Path(bpy.path.abspath(str(path)))
    else:
        raise ValueError(f"Unable to resolve path: {path}")


@dataclass
class AttributeTypeInfo:
    dname: str
    dtype: type
    width: int


@dataclass
class DomainType:
    name: str

    def __str__(self):
        return self.name


class AttributeMismatchError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


# https://docs.blender.org/api/current/bpy_types_enum_items/attribute_domain_items.html#rna-enum-attribute-domain-items
class Domains:
    POINT = DomainType(name="POINT")
    EDGE = DomainType(name="EDGE")
    FACE = DomainType(name="FACE")
    CORNER = DomainType(name="CORNER")
    CURVE = DomainType(name="CURVE")
    INSTANCE = DomainType(name="INSTNANCE")
    LAYER = DomainType(name="LAYER")


@dataclass
class AttributeType:
    type_name: str
    value_name: str
    dtype: Type
    dimensions: tuple

    def __str__(self) -> str:
        return self.type_name


# https://docs.blender.org/api/current/bpy_types_enum_items/attribute_type_items.html#rna-enum-attribute-type-items
class AttributeTypes(Enum):
    # https://docs.blender.org/api/current/bpy.types.FloatAttribute.html#bpy.types.FloatAttribute
    FLOAT = AttributeType(
        type_name="FLOAT", value_name="value", dtype=float, dimensions=(1,)
    )
    # https://docs.blender.org/api/current/bpy.types.FloatVectorAttribute.html#bpy.types.FloatVectorAttribute
    FLOAT_VECTOR = AttributeType(
        type_name="FLOAT_VECTOR", value_name="vector", dtype=float, dimensions=(3,)
    )
    # https://docs.blender.org/api/current/bpy.types.Float2Attribute.html#bpy.types.Float2Attribute
    FLOAT2 = AttributeType(
        type_name="FLOAT2", value_name="vector", dtype=float, dimensions=(2,)
    )
    # alternatively use color_srgb to get the color info in sRGB color space, otherwise linear color space
    # https://docs.blender.org/api/current/bpy.types.FloatColorAttributeValue.html#bpy.types.FloatColorAttributeValue
    FLOAT_COLOR = AttributeType(
        type_name="FLOAT_COLOR", value_name="color", dtype=float, dimensions=(4,)
    )
    # https://docs.blender.org/api/current/bpy.types.ByteColorAttribute.html#bpy.types.ByteColorAttribute
    # TODO unsure about this, int values are stored but float values are returned
    BYTE_COLOR = AttributeType(
        type_name="BYTE_COLOR", value_name="color", dtype=int, dimensions=(4,)
    )
    # https://docs.blender.org/api/current/bpy.types.QuaternionAttribute.html#bpy.types.QuaternionAttribute
    QUATERNION = AttributeType(
        type_name="QUATERNION", value_name="value", dtype=float, dimensions=(4,)
    )
    # https://docs.blender.org/api/current/bpy.types.IntAttribute.html#bpy.types.IntAttribute
    INT = AttributeType(type_name="INT", value_name="value", dtype=int, dimensions=(1,))
    # https://docs.blender.org/api/current/bpy.types.ByteIntAttributeValue.html#bpy.types.ByteIntAttributeValue
    INT8 = AttributeType(
        type_name="INT8", value_name="value", dtype=int, dimensions=(1,)
    )
    # https://docs.blender.org/api/current/bpy.types.Int2Attribute.html#bpy.types.Int2Attribute
    INT32_2D = AttributeType(
        type_name="INT32_2D", value_name="value", dtype=int, dimensions=(2,)
    )
    # https://docs.blender.org/api/current/bpy.types.Float4x4Attribute.html#bpy.types.Float4x4Attribute
    FLOAT4X4 = AttributeType(
        type_name="FLOAT4X4", value_name="value", dtype=float, dimensions=(4, 4)
    )
    # https://docs.blender.org/api/current/bpy.types.BoolAttribute.html#bpy.types.BoolAttribute
    BOOLEAN = AttributeType(
        type_name="BOOLEAN", value_name="value", dtype=bool, dimensions=(1,)
    )


def guess_atype_from_array(array: np.ndarray) -> AttributeTypes:
    """
    Determine the appropriate AttributeType based on array shape and dtype.

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
    """

    if not isinstance(array, np.ndarray):
        raise ValueError(f"`array` must be a numpy array, not {type(array)=}")

    dtype = array.dtype
    shape = array.shape
    n_row = shape[0]

    # for 1D arrays we we use the float, int of boolean attribute types
    if shape == (n_row, 1) or shape == (n_row,):
        if np.issubdtype(dtype, np.int_):
            return AttributeTypes.INT
        elif np.issubdtype(dtype, np.float_):
            return AttributeTypes.FLOAT
        elif np.issubdtype(dtype, np.bool_):
            return AttributeTypes.BOOLEAN

    # for 2D arrays we use the float_vector, float_color, float4x4 attribute types
    elif shape == (n_row, 4, 4):
        return AttributeTypes.FLOAT4X4
    elif shape == (n_row, 3):
        return AttributeTypes.FLOAT_VECTOR
    elif shape == (n_row, 4):
        return AttributeTypes.FLOAT_COLOR

    # if we didn't match against anything return float
    return AttributeTypes.FLOAT


class Attribute:
    """
    Wrapper around a Blender attribute to provide a more convenient interface with numpy arrays.

    Parameters
    ----------
    attribute : bpy.types.Attribute
        The Blender attribute to wrap.

    Attributes
    ----------
    attribute : bpy.types.Attribute
        The underlying Blender attribute.
    n_attr : int
        Number of attribute elements.
    atype : AttributeType
        Type information for the attribute.
    """

    def __init__(self, attribute: bpy.types.Attribute):
        self.attribute = attribute
        self.n_attr = len(attribute.data)
        self.atype = AttributeTypes[self.attribute.data_type].value

    @property
    def value_name(self):
        return self.atype.value_name

    @property
    def is_1d(self):
        return self.atype.dimensions == (1,)

    @property
    def type_name(self):
        return self.atype.type_name

    @property
    def shape(self):
        return (self.n_attr, *self.atype.dimensions)

    @property
    def dtype(self) -> Type:
        return self.atype.dtype

    @property
    def n_values(self) -> int:
        return np.prod(self.shape, dtype=int)

    @classmethod
    def from_object(
        cls,
        obj: bpy.types.Object,
        name: str,
        atype: AttributeType,
        domain: DomainType,
    ):
        att = obj.data.get(name)
        if att is None:
            att = obj.data.attributes.new(
                name=name, type=atype.value.type_name, domain=domain.value.name
            )
        return Attribute(att)

    def from_array(self, array: np.ndarray) -> None:
        """
        Set the attribute data from a numpy array.

        Parameters
        ----------
        array : np.ndarray
            Array containing the data to set. Must match the attribute shape.

        Raises
        ------
        ValueError
            If array shape does not match attribute shape.
        """
        if array.shape != self.shape:
            raise ValueError(
                f"Array shape {array.shape} does not match attribute shape {self.shape}"
            )

        self.attribute.data.foreach_set(self.value_name, array.reshape(-1))

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
        array = np.zeros(self.n_values, dtype=self.dtype)
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


def store_named_attribute(
    obj: bpy.types.Object,
    data: np.ndarray,
    name: str,
    atype: str | AttributeTypes | None = None,
    domain: str | DomainType = Domains.POINT,
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
    domain : str or DomainType, optional
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
    """

    if isinstance(atype, str):
        try:
            atype = AttributeTypes[atype]
        except KeyError:
            raise ValueError(
                f"Given data type {atype=} does not match any of the possible attribute types: {list(AttributeTypes)=}"
            )

    if atype is None:
        atype = guess_atype_from_array(data)

    attribute = obj.data.attributes.get(name)  # type: ignore
    if not attribute or not overwrite:
        attribute = obj.data.attributes.new(name, atype.value.type_name, str(domain))

    target_atype = AttributeTypes[attribute.data_type]
    if len(data) != len(attribute.data):
        raise NamedAttributeError(
            f"Data length {len(data)}, dimensions {data.shape} does not equal the size of the target `{domain=}`, `{len(attribute.data)=}`, {target_atype.value.dimensions=}`"
        )
    if target_atype != atype:
        raise NamedAttributeError(
            f"Attribute being written to: `{attribute.name}` of type `{target_atype.value.type_name}` does not match the type for the given data: `{atype.value.type_name}`"
        )

    # the 'foreach_set' requires a 1D array, regardless of the shape of the attribute
    # so we have to flatten it first
    attribute.data.foreach_set(atype.value.value_name, data.reshape(-1))

    # attribute bug is fixed in 4.3+
    if bpy.app.version_string.startswith("4.2"):
        # TODO remove in later updates
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


def evaluate_object(obj: bpy.types.Object):
    """
    Return an object which has the modifiers evaluated.

    Parameters
    ----------
    obj : bpy.types.Object
        The Blender object to evaluate.

    Returns
    -------
    bpy.types.Object
        The evaluated object with modifiers applied.
    """
    _check_is_mesh(obj)
    obj.update_tag()
    return obj.evaluated_get(bpy.context.evaluated_depsgraph_get())


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


def remove_named_attribute(
    obj: bpy.types.Object, name: str, domain: str | DomainType = Domains.POINT
):
    """
    Remove a named attribute from an object.

    Parameters
    ----------
    obj : bpy.types.Object
        The Blender object.
    name : str
        Name of the attribute to remove.
    domain : str or DomainType, optional
        The domain of the attribute, by default POINT.

    Raises
    ------
    AttributeError
        If the named attribute does not exist on the mesh.
    """
    _check_obj_attributes(obj)
    try:
        attr = obj.data.attributes[name]
        obj.data.attributes.remove(attr)
    except KeyError:
        raise NamedAttributeError(
            f"The selected attribute '{name}' does not exist on the object"
        )
