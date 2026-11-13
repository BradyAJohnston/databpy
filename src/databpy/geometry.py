from typing import TYPE_CHECKING, Literal, overload

import bpy
import numpy as np
from bpy.types import Context, Object

from .attribute import (
    Attribute,
    AttributeDataBlock,
    AttributeNotFoundError,
    NamedAttributeError,
    _check_array_type,
)

if TYPE_CHECKING:
    from .array import AttributeArray

GeometryComponents = Literal["MESH", "POINTCLOUD", "CURVES", "INSTANCES"]


def _is_empty(data: AttributeDataBlock) -> bool:
    if isinstance(data, bpy.types.Mesh):
        return len(data.vertices) == 0
    if isinstance(data, (bpy.types.PointCloud, bpy.types.Curves)):
        return len(data.points) == 0
    return False


def _as_array(
    name: str, attribute: Attribute, atype: "type[AttributeArray] | None"
) -> np.ndarray:
    if atype is None:
        return attribute.as_array()
    _check_array_type(name, attribute.atype, atype)
    return attribute.as_array().view(atype)


class InstanceDomainView:
    """
    Read-only dictionary-style access to the INSTANCE domain of evaluated geometry.

    Available on a `GeometrySet` as `instance`. Instance attributes only exist in
    evaluated geometry, and the values are a copy, so they can be read but not
    written.

    Examples
    --------
    ```
    geom = db.GeometrySet(obj)
    geom.instance["instance_transform", db.mat4]
    geom.instance.list_attributes()
    ```
    """

    def __init__(self, geometry: "GeometrySet"):
        self._geometry = geometry

    def _pointcloud(self) -> bpy.types.PointCloud | None:
        pointcloud = self._geometry.instances
        if pointcloud is None or len(pointcloud.points) == 0:
            return None
        return pointcloud

    def __len__(self) -> int:
        """The number of instances, 0 if the geometry doesn't have any."""
        pointcloud = self._pointcloud()
        return 0 if pointcloud is None else len(pointcloud.points)

    @overload
    def __getitem__[T: AttributeArray](self, key: tuple[str, type[T]]) -> T: ...
    @overload
    def __getitem__(self, key: str) -> np.ndarray: ...
    def __getitem__(self, key: "str | tuple[str, type[AttributeArray]]"):
        """
        Get the values of an instance attribute, as `geom.instance["name"]`.

        Index with a typed array class, as `geom.instance["name", db.mat4]`, to check
        the attribute's type and have type checkers see the array as that class.

        Raises
        ------
        AttributeNotFoundError
            If there are no instances, or the attribute doesn't exist on them.
        NamedAttributeError
            If the attribute isn't the given type.
        """
        name, atype = key if isinstance(key, tuple) else (key, None)
        pointcloud = self._pointcloud()
        if pointcloud is None or name not in pointcloud.attributes:
            raise AttributeNotFoundError(
                f"The attribute '{name}' does not exist on the instances. "
                f"Available attributes: {self.list_attributes()}"
            )
        return _as_array(name, Attribute(pointcloud.attributes[name]), atype)

    def __setitem__(self, name: str, data: np.ndarray) -> None:
        raise TypeError(
            "Instance attributes of evaluated geometry are read-only. Store them in "
            "Geometry Nodes instead."
        )

    def __contains__(self, name: str) -> bool:
        return name in self.list_attributes()

    def list_attributes(self, drop_hidden: bool = False) -> list[str]:
        """List the names of the instance attributes."""
        pointcloud = self._pointcloud()
        if pointcloud is None:
            return []
        return sorted(
            a.name
            for a in pointcloud.attributes
            if not (drop_hidden and a.name.startswith("."))
        )

    def _ipython_key_completions_(self) -> list[str]:
        return self.list_attributes()

    def __repr__(self) -> str:
        return f"<InstanceDomainView of {self._geometry.object.name!r}>"


class GeometrySet:
    """
    Access the evaluated geometry of an object (`bpy.types.GeometrySet`).

    Evaluating an object normally only exposes a single geometry data-block, but
    Geometry Nodes can output multiple components at once: a mesh, a point cloud,
    curves and instances. This class evaluates the object's modifiers and gives
    access to all of the resulting components and their attributes, for example to
    test the output of a node group.

    Parameters
    ----------
    obj : bpy.types.Object
        The Blender object to evaluate.
    context : bpy.types.Context, optional
        The context used to get the evaluated depsgraph. Defaults to `bpy.context`.

    Attributes
    ----------
    object : bpy.types.Object
        The original (unevaluated) object.
    evaluated_object : bpy.types.Object
        The evaluated object from the depsgraph.
    geometry : bpy.types.GeometrySet
        The underlying evaluated geometry.

    Notes
    -----
    The evaluated geometry is a snapshot from when the `GeometrySet` was created, and
    doesn't change when the object is changed afterwards. Its components, such as
    `mesh` and `instances`, are owned by the `GeometrySet` and freed with it, so keep
    a reference to it while using them. `db.GeometrySet(obj).mesh.vertices` raises a
    `ReferenceError`, as the `GeometrySet` is freed before the mesh is used.

    Examples
    --------
    ```{python}
    import bpy
    import databpy as db

    geom = db.GeometrySet(bpy.data.objects["Cube"])
    geom.named_attribute("position")
    ```
    ```{python}
    geom.list_attributes()
    ```

    See Also
    --------
    named_attribute : Read attribute data from an object's data-block
    evaluate_object : Evaluate an object to a single data-block
    """

    def __init__(self, obj: Object, context: Context | None = None):
        if context is None:
            context = bpy.context
        self.object = obj
        depsgraph = context.evaluated_depsgraph_get()
        self.evaluated_object: Object = depsgraph.id_eval_get(obj)
        self.geometry = self.evaluated_object.evaluated_geometry()

    @property
    def mesh(self) -> bpy.types.Mesh | None:
        """The mesh component of the evaluated geometry, if present."""
        return self.geometry.mesh

    @property
    def pointcloud(self) -> bpy.types.PointCloud | None:
        """The point cloud component of the evaluated geometry, if present."""
        return self.geometry.pointcloud

    @property
    def curves(self) -> bpy.types.Curves | None:
        """The curves component of the evaluated geometry, if present."""
        return self.geometry.curves

    @property
    def volume(self) -> bpy.types.Volume | None:
        """The volume component of the evaluated geometry, if present."""
        return self.geometry.volume

    @property
    def grease_pencil(self) -> bpy.types.GreasePencil | None:
        """The grease pencil component of the evaluated geometry, if present."""
        return self.geometry.grease_pencil

    @property
    def instances(self) -> bpy.types.PointCloud | None:
        """
        A point cloud representation of the instances component, if present.

        Each point is one instance, with attributes such as `instance_transform`
        and `.reference_index` alongside any named attributes stored on the
        instance domain.
        """
        pointcloud = self.geometry.instances_pointcloud()
        if pointcloud is not None and len(pointcloud.points):
            # Blender leaves `position` unset, so fill it from the translation of
            # each instance's transform
            transforms = Attribute(pointcloud.attributes["instance_transform"])
            position = Attribute(pointcloud.attributes["position"])
            position.from_array(transforms.as_array()[:, :3, 3])
        return pointcloud

    @property
    def instance(self) -> InstanceDomainView:
        """Read-only access to the attributes on the INSTANCE domain."""
        return InstanceDomainView(self)

    @property
    def instance_references(self) -> list:
        """The geometries, objects or collections referenced by the instances."""
        return self.geometry.instance_references()

    def components(self) -> dict[GeometryComponents, AttributeDataBlock]:
        """
        Get the attribute-holding components present in the evaluated geometry.

        Returns
        -------
        dict[GeometryComponents, AttributeDataBlock]
            A mapping of component names to their data-blocks, containing only
            the components that are present and contain geometry. Blender can
            include empty components (e.g. a 0-vertex mesh) in the evaluated
            geometry, which are excluded here; the `mesh`, `pointcloud`, `curves`
            and `instances` properties still return them.
        """
        possible: dict[GeometryComponents, AttributeDataBlock | None] = {
            "MESH": self.mesh,
            "POINTCLOUD": self.pointcloud,
            "CURVES": self.curves,
            "INSTANCES": self.instances,
        }
        return {
            name: data
            for name, data in possible.items()
            if data is not None and not _is_empty(data)
        }

    def _get_component(self, component: GeometryComponents) -> AttributeDataBlock:
        components = self.components()
        try:
            return components[component]
        except KeyError:
            raise NamedAttributeError(
                f"No {component} component in the evaluated geometry. "
                f"Present components: {list(components)}"
            )

    def list_attributes(
        self, drop_hidden: bool = False
    ) -> dict[GeometryComponents, list[str]]:
        """
        List the attribute names on each component of the evaluated geometry.

        Parameters
        ----------
        drop_hidden : bool, optional
            Whether to drop hidden attributes (those starting with a dot).
            Defaults to False.

        Returns
        -------
        dict[GeometryComponents, list[str]]
            A mapping of component names to their sorted attribute names.
        """
        return {
            name: sorted(
                attribute.name
                for attribute in data.attributes
                if not (drop_hidden and attribute.name.startswith("."))
            )
            for name, data in self.components().items()
        }

    @overload
    def named_attribute(
        self,
        name: str,
        component: GeometryComponents | None = None,
        *,
        atype: None = None,
    ) -> np.ndarray: ...
    @overload
    def named_attribute[T: AttributeArray](
        self,
        name: str,
        component: GeometryComponents | None = None,
        *,
        atype: type[T],
    ) -> T: ...
    def named_attribute(
        self,
        name: str,
        component: GeometryComponents | None = None,
        *,
        atype: "type[AttributeArray] | None" = None,
    ) -> np.ndarray:
        """
        Get named attribute data from the evaluated geometry.

        Parameters
        ----------
        name : str
            The name of the attribute.
        component : GeometryComponents, optional
            The component to read the attribute from. If None, the components are
            searched in order (MESH, POINTCLOUD, CURVES, INSTANCES) and the first
            that has the attribute is used.
        atype : type[AttributeArray] or None, optional
            The typed array class the attribute is expected to be, such as `vec3`.
            The values are returned as that class, which type checkers also see.

        Returns
        -------
        np.ndarray
            The attribute data as a numpy array, or an array of `atype` if given.

        Raises
        ------
        AttributeNotFoundError
            If the attribute does not exist on the given (or any) component.
        NamedAttributeError
            If the given component isn't present, or the attribute found isn't
            `atype`. Without a component, only the first attribute found is checked.
        """
        if component is None:
            for data in self.components().values():
                if name in data.attributes:
                    return _as_array(name, Attribute(data.attributes[name]), atype)
            raise AttributeNotFoundError(
                f"The attribute '{name}' does not exist on any component of the "
                f"evaluated geometry. Available attributes: {self.list_attributes()}"
            )

        data = self._get_component(component)
        try:
            attribute = data.attributes[name]
        except KeyError:
            raise AttributeNotFoundError(
                f"The attribute '{name}' does not exist on the {component} component. "
                f"Available attributes: {sorted(data.attributes.keys())}"
            )
        return _as_array(name, Attribute(attribute), atype)

    def __repr__(self) -> str:
        lines = [f"GeometrySet of '{self.object.name}'"]
        for name, data in self.components().items():
            if isinstance(data, bpy.types.Mesh):
                counts = (
                    f"{len(data.vertices)} verts, {len(data.edges)} edges, "
                    f"{len(data.polygons)} faces"
                )
            elif "position" in data.attributes:
                counts = f"{len(Attribute(data.attributes['position']))} points"
            else:
                counts = "empty"
            attr_names = ", ".join(
                sorted(
                    attribute.name
                    for attribute in data.attributes
                    if not attribute.name.startswith(".")
                )
            )
            lines.append(f"  {name}: {counts}")
            lines.append(f"    attributes: {attr_names}")
        for name, data in (
            ("VOLUME", self.volume),
            ("GREASE_PENCIL", self.grease_pencil),
        ):
            if data is not None:
                lines.append(f"  {name}: present")
        return "\n".join(lines)
