from .object import (
    ObjectTracker,
    BlenderObject,
    create_object,
    create_bob,
    LinkedObjectError,
    bdo,
)
from .vdb import import_vdb
import bpy
from .utils import centre, lerp
from .attribute import (
    named_attribute,
    store_named_attribute,
    Attribute,
    AttributeType,
    AttributeTypeInfo,
    AttributeTypes,
    Domains,
    DomainType,
)


def register():
    bpy.types.Object.uuid = bpy.props.StringProperty(
        name="UUID",
        description="Unique identifier for the object",
        default="",
        options={"HIDDEN"},
    )


def unregister():
    del bpy.types.Object.uuid
