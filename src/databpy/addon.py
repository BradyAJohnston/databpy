import uuid
import warnings

import bpy
from bpy.app.handlers import persistent

# Persistent identifier for objects tracked by databpy. Stored as a plain custom
# property so it needs no registration and is saved with the .blend file. The leading
# underscore hides it from the Custom Properties panel.
UUID_KEY = "_databpy_uuid"

LEGACY_REMOVAL_VERSION = "0.11.0"

# Changes on every file load and is unique per process, so `session_uid` values cached
# in a previous session (or a pickled wrapper) are never trusted in the current one.
_session_token = uuid.uuid4().hex


def session_token() -> str:
    return _session_token


def find_by_session_uid(
    session_uid: int, name_hint: str = ""
) -> bpy.types.Object | None:
    """Find an object by its `session_uid`, checking `name_hint` first as a fast path."""
    obj = bpy.data.objects.get(name_hint)
    if obj is not None and obj.session_uid == session_uid:
        return obj
    for obj in bpy.data.objects:
        if obj.session_uid == session_uid:
            return obj
    return None


@persistent
def _databpy_load_post(*args) -> None:
    global _session_token
    _session_token = uuid.uuid4().hex


def _install_load_handler() -> None:
    handlers = bpy.app.handlers.load_post
    # replace a handler left over from a previous import of this module (add-on reload)
    for handler in list(handlers):
        if getattr(handler, "__name__", None) == _databpy_load_post.__name__:
            handlers.remove(handler)
    handlers.append(_databpy_load_post)


_install_load_handler()


def _ensure_legacy_property() -> None:
    # databpy < 0.9 stored the uuid in a registered `Object.uuid` property. It is kept
    # registered (and in sync) during the deprecation window so values in existing
    # .blend files can be migrated and downstream code reading `obj.uuid` keeps working
    if not hasattr(bpy.types.Object, "uuid"):
        bpy.types.Object.uuid = bpy.props.StringProperty(  # type: ignore
            name="UUID",
            description="Unique identifier for the object",
            default="",
            options={"HIDDEN"},
        )


def get_uuid(obj: bpy.types.Object) -> str:
    """Return the persistent databpy uuid of an object, or "" if it has none."""
    value = obj.get(UUID_KEY)
    if value is not None:
        return value

    _ensure_legacy_property()
    value = obj.uuid  # type: ignore
    if value:
        try:
            obj[UUID_KEY] = value
        except (AttributeError, TypeError):
            # linked library data or a restricted context can't be written to, the
            # legacy value is still valid for this lookup
            pass
    return value


def set_uuid(obj: bpy.types.Object, value: str) -> None:
    """Set the persistent databpy uuid of an object."""
    obj[UUID_KEY] = value
    _ensure_legacy_property()
    obj.uuid = value  # type: ignore


def register() -> None:
    """
    Deprecated: databpy no longer needs registering.

    Objects are identified through a plain custom property, which requires no
    registration.
    """
    warnings.warn(
        "`databpy.register()` is no longer required and will be removed in databpy "
        f"{LEGACY_REMOVAL_VERSION}.",
        FutureWarning,
        stacklevel=2,
    )
    _ensure_legacy_property()


def unregister() -> None:
    """
    Deprecated: this is now a no-op.

    databpy is shared between add-ons, so removing `Object.uuid` from one add-on would
    break every other add-on that uses databpy.
    """
    warnings.warn(
        "`databpy.unregister()` no longer does anything and will be removed in databpy "
        f"{LEGACY_REMOVAL_VERSION}. It previously removed `Object.uuid`, which broke "
        "other add-ons using databpy.",
        FutureWarning,
        stacklevel=2,
    )
