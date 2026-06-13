import bpy


def register():
    bpy.types.Object.uuid = bpy.props.StringProperty(
        name="UUID",
        description="Unique identifier for the object",
        default="",
        options={"HIDDEN"},
    )


def unregister():
    del bpy.types.Object.uuid
