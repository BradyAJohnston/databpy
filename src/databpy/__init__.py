from typing import TYPE_CHECKING

from . import collection, utils
from .addon import register, unregister
from .array import (
    AttributeArray,
    boolean,
    color,
    color8,
    float32,
    int8,
    int32,
    ivec2,
    mat4,
    quat,
    sivec2,
    srgb,
    string,
    vec2,
    vec3,
    vec4,
)
from .attribute import (
    Attribute,
    AttributeDomains,
    AttributeMismatchError,
    AttributeNotFoundError,
    AttributeType,
    AttributeTypes,
    NamedAttributeError,
    evaluate_object,
    list_attributes,
    named_attribute,
    remove_named_attribute,
    store_named_attribute,
)
from .collection import create_collection, move_to_collection
from .errors import DatabpyError
from .geometry import GeometrySet, InstanceDomainView
from .object import (
    BOB,
    AttributeDomainView,
    BlenderObject,
    BlenderObjectAttribute,
    BlenderObjectBase,
    LinkedObjectError,
    ObjectTracker,
    bdo,
    create_bob,
    create_curves_object,
    create_grease_pencil_object,
    create_mesh_object,
    create_object,
    create_pointcloud_object,
)
from .utils import (
    active_object,
    active_scene,
    centre,
    curves_data,
    lerp,
    mesh_data,
    pointcloud_data,
    require,
    require_data,
    volume_data,
)
from .vdb import import_vdb

__all__ = [
    "BOB",
    "Attribute",
    "AttributeArray",
    "AttributeDomainView",
    "AttributeDomains",
    "AttributeMismatchError",
    "AttributeNotFoundError",
    "AttributeType",
    "AttributeTypes",
    "BlenderObject",
    "BlenderObjectAttribute",
    "BlenderObjectBase",
    "DatabpyError",
    "GeometrySet",
    "InstanceDomainView",
    "LinkedObjectError",
    "NamedAttributeError",
    "ObjectTracker",
    "active_object",
    "active_scene",
    "bdo",
    "boolean",
    "centre",
    "collection",
    "color",
    "color8",
    "create_bob",
    "create_collection",
    "create_curves_object",
    "create_grease_pencil_object",
    "create_mesh_object",
    "create_object",
    "create_pointcloud_object",
    "curves_data",
    "evaluate_object",
    "float32",
    "import_vdb",
    "int8",
    "int32",
    "ivec2",
    "lerp",
    "list_attributes",
    "mat4",
    "mesh_data",
    "move_to_collection",
    "named_attribute",
    "pointcloud_data",
    "quat",
    "register",
    "remove_named_attribute",
    "require",
    "require_data",
    "sivec2",
    "srgb",
    "store_named_attribute",
    "string",
    "unregister",
    "utils",
    "vec2",
    "vec3",
    "vec4",
    "volume_data",
]


if TYPE_CHECKING:
    from . import nodes as nodes


def __getattr__(name: str):
    # the deprecated `nodes` module is only imported when it is used, which warns
    if name == "nodes":
        import importlib

        return importlib.import_module(".nodes", __name__)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
