from typing import Literal

import bpy
import numpy as np
from bpy.types import Context, Object

from .attribute import Attribute, NamedAttributeError

GeometryComponents = Literal["MESH", "POINTCLOUD", "CURVES", "INSTANCES"]


def _is_empty(data: bpy.types.ID) -> bool:
    if isinstance(data, bpy.types.Mesh):
        return len(data.vertices) == 0
    if isinstance(data, (bpy.types.PointCloud, bpy.types.Curves)):
        return len(data.points) == 0
    return False


class GeometrySet:
    """
    Access the evaluated geometry of an object (`bpy.types.GeometrySet`).

    Evaluating an object normally only exposes a single geometry data-block, but
    Geometry Nodes can output multiple components at once - a mesh, a point cloud,
    curves and instances. This class evaluates the object's modifiers and provides
    access to all of the resulting components and their attributes, which is
    particularly useful for testing node group outputs.

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
        return self.geometry.instances_pointcloud()

    @property
    def instance_references(self) -> list:
        """The geometries, objects or collections referenced by the instances."""
        return self.geometry.instance_references()

    def components(self) -> dict[GeometryComponents, bpy.types.ID]:
        """
        Get the attribute-holding components present in the evaluated geometry.

        Returns
        -------
        dict[GeometryComponents, bpy.types.ID]
            A mapping of component names to their data-blocks, containing only
            the components that are present and contain geometry. Blender can
            include empty components (e.g. a 0-vertex mesh) in the evaluated
            geometry, which are excluded here - access the `mesh` etc. properties
            directly if you need them.
        """
        possible: dict[GeometryComponents, bpy.types.ID | None] = {
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

    def _get_component(self, component: GeometryComponents) -> bpy.types.ID:
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
                key
                for key in data.attributes.keys()
                if not (drop_hidden and key.startswith("."))
            )
            for name, data in self.components().items()
        }

    def named_attribute(
        self, name: str, component: GeometryComponents | None = None
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

        Returns
        -------
        np.ndarray
            The attribute data as a numpy array.

        Raises
        ------
        NamedAttributeError
            If the attribute does not exist on the given (or any) component.
        """
        if component is None:
            for data in self.components().values():
                if name in data.attributes:
                    return Attribute(data.attributes[name]).as_array()
            raise NamedAttributeError(
                f"The attribute '{name}' does not exist on any component of the "
                f"evaluated geometry. Available attributes: {self.list_attributes()}"
            )

        data = self._get_component(component)
        try:
            attribute = data.attributes[name]
        except KeyError:
            raise NamedAttributeError(
                f"The attribute '{name}' does not exist on the {component} component. "
                f"Available attributes: {sorted(data.attributes.keys())}"
            )
        return Attribute(attribute).as_array()

    def __repr__(self) -> str:
        lines = [f"GeometrySet of '{self.object.name}'"]
        for name, data in self.components().items():
            if isinstance(data, bpy.types.Mesh):
                counts = (
                    f"{len(data.vertices)} verts, {len(data.edges)} edges, "
                    f"{len(data.polygons)} faces"
                )
            elif "position" in data.attributes:
                counts = f"{len(data.attributes['position'].data)} points"
            else:
                counts = "empty"
            attr_names = ", ".join(
                sorted(key for key in data.attributes.keys() if not key.startswith("."))
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
