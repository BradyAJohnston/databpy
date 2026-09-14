import bpy

# the `uuid` property is registered dynamically on `bpy.types.Object`, so it isn't
# part of the static type information for `Object`. All runtime access goes through
# `setattr` / `getattr` with this constant (see `databpy.object.get_uuid` / `set_uuid`)
UUID_PROP_NAME = "uuid"


def register():
    setattr(
        bpy.types.Object,
        UUID_PROP_NAME,
        bpy.props.StringProperty(
            name="UUID",
            description="Unique identifier for the object",
            default="",
            options={"HIDDEN"},
        ),
    )


def unregister():
    delattr(bpy.types.Object, UUID_PROP_NAME)
