from uuid import uuid1
import warnings

import bpy
import numpy as np
from bpy.types import Object
from numpy import typing as npt
from .array import AttributeArray

from . import attribute as attr
from .addon import register
from .attribute import (
    AttributeDomains,
    AttributeTypes,
    PossibleAttributeTypes,
    DomainNames,
    AttributeTypeNames,
    list_attributes,
    _check_obj_attributes,
    evaluate_object,
    Attribute,
)
from .collection import create_collection


class LinkedObjectError(Exception):
    """
    Error raised when a Python object doesn't have a linked object in the 3D scene.

    Parameters
    ----------
    message : str
        The error message describing why the linked object is missing or invalid.

    Attributes
    ----------
    message : str
        The error message that was passed.
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class ObjectDatabase:
    def __getitem__(self, key: str) -> Object:
        """
        Get an object from the database using its name.

        A helper for typing in development

        Parameters
        ----------
        key : str
            The name of the object to get.

        Returns
        -------
        Object
            The object from the bpy.data.objects database
        """
        return bpy.data.objects[key]


bdo = ObjectDatabase()


class ObjectTracker:
    """
    A context manager for tracking new objects in Blender.

    This class provides a way to track new objects that are added to Blender's bpy.data.objects collection.
    It stores the current objects when entering the context and provides a method to find new objects that were added when exiting the context.

    Methods
    -------
    new_objects()
        Returns a list of new objects that were added to bpy.data.objects while in the context.
    """

    def __enter__(self):
        """
        Store the current objects and their names when entering the context.

        Returns
        -------
        self
            The instance of the class.
        """
        self.objects = list(bpy.context.scene.objects)  # type: ignore
        return self

    def __exit__(self, type, value, traceback):
        pass

    def new_objects(self):
        """
        Find new objects that were added to bpy.data.objects while in the context.

        Use new_objects()[-1] to get the most recently added object.

        Returns
        -------
        list
            A list of new objects.
        """
        obj_names = list([o.name for o in self.objects])
        current_objects = bpy.context.scene.objects  # type: ignore
        new_objects = []
        for obj in current_objects:
            if obj.name not in obj_names:
                new_objects.append(obj)
        return new_objects

    def latest(self):
        """
        Get the most recently added object.

        This method returns the most recently added object to bpy.data.objects while in the context.

        Returns
        -------
        Object
            The most recently added object.
        """
        return self.new_objects()[-1]


def get_from_uuid(uuid: str) -> Object:
    """
    Get an object from the bpy.data.objects collection using a UUID.

    Parameters
    ----------
    uuid : str
        The UUID of the object to get.

    Returns
    -------
    Object
        The object from the bpy.data.objects collection.
    """
    for obj in bpy.data.objects:
        if obj.uuid == uuid:  # type: ignore
            return obj

    raise LinkedObjectError(
        "Failed to find an object in the database with given uuid: " + uuid
    )


class BlenderObjectBase:
    """
    Minimal base class for Blender objects with name and object access.

    This provides a minimal set of functionality to persistently track a an object in
    Blender's database, providing access to it's name property and also the object itself.
    Referencing an object in the database directly can lead to ReferenceErrors as Blender
    can _without warning_ alter the database and thus the Object's place in memory.

    To get around this BlenderObjectBase always looks up via the name attribute and
    double checks with the `uuid` attribute to ensure the correct object is being returned.
    If there is a mismatch the entite database will be searched for an object with a uuid
    that matches and if none is found a LinkedObjectError will be raised.

    Blender _internally_ uses it's own UUID / reference system but this is currently (and
    frustratingly) not available to us via the Python API.

    Attributes
    ----------
    object : bpy.types.Object
        The wrapped Blender object.
    uuid : str
        Unique identifier for this object instance.
    name : str
        Name of the Blender object.
    """

    def __init__(self, obj: Object | str | None = None):
        """
        Initialize the BlenderObjectBase.

        Parameters
        ----------
        obj : Object | str | None
            The Blender object to wrap.
        """
        self._uuid: str = str(uuid1())
        self._object_name: str = ""

        if not hasattr(bpy.types.Object, "uuid"):
            register()

        if isinstance(obj, Object):
            if obj.uuid != "":  # type: ignore
                self._uuid = obj.uuid  # type: ignore
            self.object = obj
        elif isinstance(obj, str):
            obj = bpy.data.objects[obj]
            if obj.uuid != "":  # type: ignore
                self._uuid = obj.uuid  # type: ignore
            self.object = obj
        elif obj is None:
            self._object_name = ""

    @property
    def object(self) -> Object:
        """
        Get the Blender object.

        Returns
        -------
        Object | None
            The Blender object, or None if not found.
        """

        # if we can't match a an object by name in the database, we instead try to match
        # by the uuid. If we match by name and the uuid doesn't match, we try to find
        # another object instead with the same uuid

        try:
            obj = bpy.data.objects[self._object_name]
            if obj.uuid != self.uuid:  # type: ignore
                obj = get_from_uuid(self.uuid)
        except (KeyError, MemoryError):
            obj = get_from_uuid(self.uuid)
            self._object_name = obj.name

        return obj

    @object.setter
    def object(self, value: Object) -> None:
        """
        Set the Blender object.

        Parameters
        ----------
        value : Object
            The Blender object to set.
        """

        if not isinstance(value, Object):
            raise ValueError(f"{value} must be a bpy.types.Object")

        try:
            value.uuid = self.uuid  # type: ignore
        except AttributeError:
            register()
            value.uuid = self.uuid  # type: ignore
        self._object_name = value.name

    @property
    def uuid(self) -> str:
        """
        Get the unique identifier for this object.

        Returns
        -------
        str
            The UUID string for this object.
        """
        return self._uuid

    @property
    def name(self) -> str:
        """
        Get the name of the Blender object.

        Returns
        -------
        str
            The name of the Blender object.
        """
        return self.object.name

    @name.setter
    def name(self, value: str) -> None:
        """
        Set the name of the Blender object.

        Parameters
        ----------
        value : str
            The name to set for the Blender object.
        """
        obj = self.object
        obj.name = value
        self._object_name = obj.name


class BlenderObjectAttribute(BlenderObjectBase):
    """
    Minimal base class for Blender objects with attribute access.

    This class provides core functionality for storing and accessing named attributes
    on Blender objects.

    It is intended for use with Mesh, PointCloud and Curves type objects for easier and
    "numpy-like" attribute access.

    It can be inherited by other classes for easier attribute management on objects.

    Attributes
    ----------
    position : AttributeArray
        Position attribute of the object's vertices/points.
    data : bpy.types.Mesh | bpy.types.Curves | bpy.types.PointCloud
        The data block associated with this object.
    attributes
        Get the attributes collection of the Blender object.
    """

    def store_named_attribute(
        self,
        data: np.ndarray,
        name: str,
        atype: AttributeTypeNames | AttributeTypes | None = None,
        domain: DomainNames | AttributeDomains = AttributeDomains.POINT,
    ) -> None:
        """
        Store a named attribute on the Blender object.

        Parameters
        ----------
        data : np.ndarray
            The data to be stored as an attribute.
        name : str
            The name for the attribute. Will overwrite an already existing attribute.
        atype : str or AttributeType or None, optional
            The attribute type to store the data as. Either string or selection from the
            AttributeTypes enum. None will attempt to infer the attribute type from the
            input array.
        domain : str or AttributeDomain, optional
            The domain to store the attribute on. Defaults to Domains.POINT.

        Returns
        -------
        self
        """
        self._check_obj()
        attr.store_named_attribute(
            self.object, data=data, name=name, atype=atype, domain=domain
        )

    def remove_named_attribute(self, name: str) -> None:
        """
        Remove a named attribute from the object.

        Parameters
        ----------
        name : str
            The name of the attribute to remove.
        """
        self._check_obj()
        attr.remove_named_attribute(self.object, name=name)

    def named_attribute(self, name: str, evaluate: bool = False) -> np.ndarray:
        """
        Retrieve a named attribute from the object.

        Optionally, evaluate the object before reading the named attribute

        Parameters
        ----------
        name : str
            Name of the attribute to get.
        evaluate : bool, optional
            Whether to evaluate the object before reading the attribute (default is False).
        Returns
        -------
        np.ndarray
            The attribute read from the mesh as a numpy array.
        """
        self._check_obj()
        return attr.named_attribute(self.object, name=name, evaluate=evaluate)

    @property
    def data(self):
        """
        Get the data block of the Blender object.

        Returns
        -------
        bpy.types.Mesh | bpy.types.Curves | bpy.types.PointCloud
            The data block associated with this object (e.g., mesh data, curves data, or point cloud data).
        """
        return self.object.data

    @property
    def attributes(self):
        """
        Get the attributes of the Blender object.

        Returns
        -------
        bpy.types.Attributes
            The attributes of the Blender object.
        """
        return self.data.attributes  # type: ignore

    @property
    def position(self) -> AttributeArray:
        """
        Get the position of the vertices of the Blender object.

        Returns
        -------
        PositionArray
            A numpy array subclass that automatically syncs changes back to Blender.

        Examples
        --------
        ```
        # Regular array operations
        pos = bob.position
        pos[0] = [1, 2, 3]  # Set position of first vertex

        # Column operations will be intercepted automatically
        pos[:, 2] = 5.0  # Set all Z coordinates to 5.0
        ```
        """
        return AttributeArray(self.object, "position")

    @position.setter
    def position(self, value: np.ndarray) -> None:
        """
        Set the position of the vertices of the Blender object.

        Parameters
        ----------
        value : np.ndarray
            The position to set for the vertices of the Blender object.
        """
        self.store_named_attribute(
            value,
            name="position",
            atype=AttributeTypes.FLOAT_VECTOR,
            domain=AttributeDomains.POINT,
        )

    def list_attributes(
        self, evaluate: bool = False, drop_hidden: bool = False
    ) -> list[str]:
        """
        Returns a list of attribute names for the object.

        Parameters
        ----------
        evaluate : bool, optional
            Whether to first evaluate the modifiers on the object before listing the
            available attributes.
        drop_hidden : bool, optional
            Whether to drop hidden attributes (those starting with a dot). Defaults to False.

        Returns
        -------
        list[str] | None
            A list of attribute names if the molecule object exists, None otherwise.
        """
        return list_attributes(self.object, evaluate=evaluate, drop_hidden=drop_hidden)

    def __len__(self) -> int:
        """
        Get the number of points in the Blender object.

        For meshes, this returns the number of vertices. For point clouds, this
        returns the number of points. For curves (new Curves type), this returns
        the number of control points.

        Note: Only supports Mesh, Curves (new), and PointCloud types.
        Does not support the legacy Curve type.

        Returns
        -------
        int
            The number of points in the Blender object.
        """
        if isinstance(self.data, bpy.types.Mesh):
            return len(self.data.vertices)
        elif isinstance(self.data, bpy.types.PointCloud):
            return len(self.data.points)
        elif isinstance(self.data, bpy.types.Curves):
            if "position" in self.data.attributes:
                return len(self.data.attributes["position"].data)  # type: ignore
            return 0
        else:
            raise TypeError(
                f"Object type {type(self.data).__name__} is not supported. "
                f"Supported types: Mesh, Curves, PointCloud"
            )

    def _ipython_key_completions_(self) -> list[str]:
        """
        Return possible named attributes for IPython tab completion.

        Returns
        -------
        list[str]
            List of attribute names available on this object.
        """
        return self.list_attributes()

    def __getitem__(self, name: str) -> AttributeArray:
        """
        Access a named attribute using dictionary-style syntax.

        Parameters
        ----------
        name : str
            The name of the attribute to access.

        Returns
        -------
        AttributeArray
            An AttributeArray that wraps the named attribute data.

        Raises
        ------
        ValueError
            If name is not a string.
        """
        if not isinstance(name, str):
            raise ValueError("Attribute name must be a string")
        return AttributeArray(self.object, name)

    def __setitem__(self, name: str, data: np.ndarray) -> None:
        """
        Set a named attribute using dictionary-style syntax.

        Parameters
        ----------
        name : str
            The name of the attribute to set.
        data : np.ndarray
            The data to store in the attribute.
        """
        if name in self.list_attributes():
            att = Attribute(self.attributes[name])  # type: ignore
            self.store_named_attribute(
                data=data, name=name, domain=att.domain, atype=att.atype
            )
        self.store_named_attribute(data=data, name=name)

    def _check_obj(self) -> None:
        _check_obj_attributes(self.object)

    def evaluate(self) -> Object:
        """
        Return a version of the object with all modifiers applied.

        Returns
        -------
        Object
            A new Object that isn't yet registered with the database
        """
        return evaluate_object(self.object)


class BlenderObject(BlenderObjectAttribute):
    """
    A convenience class for working with Blender objects.

    Extends BlenderObjectBase with creation methods and additional utility functions.
    """

    @classmethod
    def from_mesh(
        cls,
        vertices: np.ndarray | None = None,
        edges: np.ndarray | None = None,
        faces: np.ndarray | None = None,
        name: str = "Mesh",
        collection: bpy.types.Collection | None = None,
    ) -> "BlenderObject":
        """
        Create a BlenderObject from mesh data.

        Parameters
        ----------
        vertices : ndarray or None, optional
            Array of vertex coordinates with shape (N, 3).
            Default is None.
        edges : ndarray or None, optional
            Array of edge indices.
            Default is None.
        faces : ndarray or None, optional
            Array of face indices.
            Default is None.
        name : str, optional
            Name of the created object.
            Default is "Mesh".
        collection : bpy.types.Collection or None, optional
            Blender collection to link the object to.
            Default is None.

        Returns
        -------
        BlenderObject
            A wrapped Blender mesh object.

        Examples
        --------
        ```python
        import numpy as np
        import databpy as db

        vertices = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]])
        bob = db.BlenderObject.from_mesh(vertices=vertices, name="MyMesh")
        print(len(bob))  # 4
        ```
        """
        obj = create_mesh_object(
            vertices=vertices,
            edges=edges,
            faces=faces,
            name=name,
            collection=collection,
        )
        return cls(obj)

    @classmethod
    def from_curves(
        cls,
        positions: np.ndarray | None = None,
        curve_sizes: list[int] | np.ndarray | None = None,
        name: str = "Curves",
        collection: bpy.types.Collection | None = None,
    ) -> "BlenderObject":
        """
        Create a BlenderObject from curves data.

        Parameters
        ----------
        positions : ndarray or None, optional
            Control point positions with shape (N, 3).
            Default is None.
        curve_sizes : list[int] | np.ndarray or None, optional
            Number of points in each curve.
            Default is None.
        name : str, optional
            Name of the created object.
            Default is "Curves".
        collection : bpy.types.Collection or None, optional
            Blender collection to link the object to.
            Default is None.

        Returns
        -------
        BlenderObject
            A wrapped Blender curves object.

        Examples
        --------
        ```python
        import numpy as np
        import databpy as db

        # Create 2 curves with 3 and 4 points
        positions = np.random.random((7, 3))
        bob = db.BlenderObject.from_curves(positions, [3, 4], name="MyCurves")
        print(len(bob))  # 7
        ```
        """
        obj = create_curves_object(
            positions=positions,
            curve_sizes=curve_sizes,
            name=name,
            collection=collection,
        )
        return cls(obj)

    @classmethod
    def from_pointcloud(
        cls,
        positions: np.ndarray | None = None,
        name: str = "PointCloud",
        collection: bpy.types.Collection | None = None,
    ) -> "BlenderObject":
        """
        Create a BlenderObject from point cloud data.

        Parameters
        ----------
        positions : ndarray or None, optional
            Point positions with shape (N, 3).
            Default is None.
        name : str, optional
            Name of the created object.
            Default is "PointCloud".
        collection : bpy.types.Collection or None, optional
            Blender collection to link the object to.
            Default is None.

        Returns
        -------
        BlenderObject
            A wrapped Blender point cloud object.

        Examples
        --------
        ```python
        import numpy as np
        import databpy as db

        # Create point cloud with 100 random points
        positions = np.random.random((100, 3))
        bob = db.BlenderObject.from_pointcloud(positions, name="MyPointCloud")
        print(len(bob))  # 100
        ```
        """
        obj = create_pointcloud_object(
            positions=positions,
            name=name,
            collection=collection,
        )
        return cls(obj)

    def new_from_pydata(
        self,
        vertices: npt.ArrayLike | None = None,
        edges: npt.ArrayLike | None = None,
        faces: npt.ArrayLike | None = None,
    ) -> Object:
        """
        Create a new Blender object from vertex, edge and face data.

        Parameters
        ----------
        vertices : np.ndarray
            The vertices of the object.
        edges : np.ndarray
            The edges of the object.
        faces : np.ndarray
            The faces of the object.

        Returns
        -------
        Object
            The new Blender object.
        """
        if not isinstance(self.data, bpy.types.Mesh):
            raise TypeError(
                f"Object must be a mesh to create a new object from pydata, not {type(self.data)}"
            )
        vertices, edges, faces = [
            [] if x is None else x for x in (vertices, edges, faces)
        ]
        self.data.clear_geometry()
        self.data.from_pydata(vertices, edges, faces)
        return self.object

    def centroid(self, weight: str | np.ndarray | None = None) -> np.ndarray:
        """
        Calculate the weighted or unweighted centroid of the object's positions.

        Parameters
        ----------
        weight : str | np.ndarray | None, optional
            The weights or indices for calculating the centroid:
            - If str: Name of attribute to use as weights
            - If np.ndarray with float dtype: Weights for each position
            - If np.ndarray with int dtype: Indices of positions to include
            - If None: Use all positions equally weighted
            Defaults to None.

        Returns
        -------
        np.ndarray
            A 3D vector representing the centroid position.
        """
        if isinstance(weight, str):
            weight = self.named_attribute(weight)

        if isinstance(weight, np.ndarray):
            if weight.dtype.kind == "f":
                return np.average(self.position, weights=weight, axis=0)
            elif weight.dtype.kind == "i":
                return np.average(self.position[weight], axis=0)

        return np.average(self.position, axis=0)

    @property
    def vertices(self):
        """
        Get the vertices of the Blender mesh object.

        .. deprecated:: 0.5.0
            This property is mesh-specific and will be removed in version 1.0.0.
            Use ``bob.data.vertices`` directly for mesh objects, or use
            the attribute system (``bob['position']`` or ``bob.named_attribute('position')``)
            which works across all geometry types.

        Returns
        -------
        bpy.types.Vertices
            The vertices of the mesh object.

        Raises
        ------
        AttributeError
            If the object is not a mesh.
        """
        warnings.warn(
            "BlenderObject.vertices is deprecated and will be removed in version 1.0.0. "
            "Use bob.data.vertices for mesh objects, or bob['position'] for "
            "geometry-agnostic attribute access.",
            DeprecationWarning,
            stacklevel=2,
        )
        if not isinstance(self.data, bpy.types.Mesh):
            raise AttributeError(
                f"vertices property only works with Mesh objects, "
                f"not {type(self.data).__name__}"
            )
        return self.data.vertices

    @property
    def edges(self):
        """
        Get the edges of the Blender mesh object.

        .. deprecated:: 0.5.0
            This property is mesh-specific and will be removed in version 1.0.0.
            Use ``bob.data.edges`` directly for mesh objects.

        Returns
        -------
        bpy.types.Edges
            The edges of the mesh object.

        Raises
        ------
        AttributeError
            If the object is not a mesh.
        """
        warnings.warn(
            "BlenderObject.edges is deprecated and will be removed in version 1.0.0. "
            "Use bob.data.edges directly for mesh objects.",
            DeprecationWarning,
            stacklevel=2,
        )
        if not isinstance(self.data, bpy.types.Mesh):
            raise AttributeError(
                f"edges property only works with Mesh objects, "
                f"not {type(self.data).__name__}"
            )
        return self.data.edges


def create_mesh_object(
    vertices: npt.ArrayLike | None = None,
    edges: npt.ArrayLike | None = None,
    faces: np.ndarray | None = None,
    name: str = "Mesh",
    collection: bpy.types.Collection | None = None,
) -> Object:
    """
    Create a new Blender mesh object.

    Parameters
    ----------
    vertices : np.ndarray, optional
        The vertices as a numpy array with shape (N, 3). Defaults to None.
    edges : np.ndarray, optional
        The edges as a numpy array. Defaults to None.
    faces : np.ndarray, optional
        The faces as a numpy array. Defaults to None.
    name : str, optional
        The name of the object. Defaults to 'Mesh'.
    collection : bpy.types.Collection, optional
        The collection to link the object to. Defaults to None.

    Returns
    -------
    Object
        The created mesh object.
    """

    def _array(a):
        if a is None:
            return []
        else:
            return np.asarray(a)

    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(
        vertices=_array(vertices), edges=_array(edges), faces=_array(faces)
    )
    obj = bpy.data.objects.new(name, mesh)
    if collection is None:
        collection = create_collection("Collection")
    collection.objects.link(obj)
    return obj


def create_curves_object(
    positions: np.ndarray | None = None,
    curve_sizes: list[int] | np.ndarray | None = None,
    name: str = "Curves",
    collection: bpy.types.Collection | None = None,
) -> Object:
    """
    Create a new Blender curves object (new Curves type, not legacy Curve).

    Parameters
    ----------
    positions : np.ndarray, optional
        The control point positions as a numpy array with shape (N, 3).
        If None, creates an empty curves object. Defaults to None.
    curve_sizes : list[int] | np.ndarray, optional
        Number of points in each curve. For example, [4, 5, 6] creates
        3 curves with 4, 5, and 6 control points respectively.
        Total must equal len(positions). If None, creates an empty curves
        object. Defaults to None.
    name : str, optional
        The name of the object. Defaults to 'Curves'.
    collection : bpy.types.Collection, optional
        The collection to link the object to. Defaults to None.

    Returns
    -------
    Object
        The created curves object.

    Raises
    ------
    ValueError
        If positions and curve_sizes lengths don't match.

    Examples
    --------
    ```python
    import numpy as np
    from databpy import create_curves_object

    # Create 2 curves with 3 and 4 points
    positions = np.random.random((7, 3))
    curves_obj = create_curves_object(positions, [3, 4])
    ```
    """
    curves_data = bpy.data.hair_curves.new(name)
    obj = bpy.data.objects.new(name, curves_data)

    if collection is None:
        collection = create_collection("Collection")
    collection.objects.link(obj)

    # If positions and curve_sizes are provided, add the curves
    if positions is not None and curve_sizes is not None:
        positions = np.asarray(positions)
        curve_sizes = np.asarray(curve_sizes, dtype=int)

        total_points = np.sum(curve_sizes)
        if len(positions) != total_points:
            raise ValueError(
                f"Total points in curve_sizes ({total_points}) must equal "
                f"number of positions ({len(positions)})"
            )

        curves_data.add_curves(curve_sizes.tolist())
        attr.store_named_attribute(obj, positions, "position")

    return obj


def create_pointcloud_object(
    positions: np.ndarray | None = None,
    name: str = "PointCloud",
    collection: bpy.types.Collection | None = None,
) -> Object:
    """
    Create a new Blender point cloud object.

    This function creates a point cloud by first creating a mesh with vertices
    at the specified positions, then converting it to a point cloud using
    Blender's convert operator.

    Parameters
    ----------
    positions : np.ndarray, optional
        The point positions as a numpy array with shape (N, 3).
        If None, creates an empty point cloud object. Defaults to None.
    name : str, optional
        The name of the object. Defaults to 'PointCloud'.
    collection : bpy.types.Collection, optional
        The collection to link the object to. Defaults to None.

    Returns
    -------
    Object
        The created point cloud object.

    Examples
    --------
    ```python
    import numpy as np
    from databpy import create_pointcloud_object

    # Create point cloud with 100 random points
    positions = np.random.random((100, 3))
    pc_obj = create_pointcloud_object(positions, name="MyPC")
    print(len(pc_obj.data.points))  # 100
    ```

    Notes
    -----
    This function works by creating a temporary mesh and converting it to a
    point cloud using `bpy.ops.object.convert(target='POINTCLOUD')`.
    """

    obj = create_mesh_object(
        vertices=positions, edges=None, faces=None, name=name, collection=collection
    )

    with bpy.context.temp_override(  # type: ignore
        active_object=obj,
        selected_objects=[obj],
        selected_editable_objects=[obj],
    ):
        bpy.ops.object.convert(target="POINTCLOUD")

    return obj


def create_object(
    vertices: npt.ArrayLike | None = None,
    edges: npt.ArrayLike | None = None,
    faces: np.ndarray | None = None,
    name: str = "NewObject",
    collection: bpy.types.Collection | None = None,
) -> Object:
    """
    Create a new Blender mesh object.

    Parameters
    ----------
    vertices : np.ndarray, optional
        The vertices as a numpy array. Defaults to None.
    edges : np.ndarray, optional
        The edges as a numpy array. Defaults to None.
    faces : np.ndarray, optional
        The faces as a numpy array. Defaults to None.
    name : str, optional
        The name of the object. Defaults to 'NewObject'.
    collection : bpy.types.Collection, optional
        The collection to link the object to. Defaults to None.

    Returns
    -------
    Object
        The created mesh object.
    """
    return create_mesh_object(vertices, edges, faces, name, collection)


def create_bob(
    vertices: np.ndarray | None = None,
    edges: np.ndarray | None = None,
    faces: np.ndarray | None = None,
    name: str = "NewObject",
    collection: bpy.types.Collection | None = None,
    uuid: str | None = None,
) -> BlenderObject:
    """
    Create a BlenderObject wrapper around a new Blender mesh object.

    Parameters
    ----------
    vertices : ndarray or None, optional
        Array of vertex coordinates.
        Default is None.
    edges : ndarray or None, optional
        Array of edge indices.
        Default is None.
    faces : ndarray or None, optional
        Array of face indices.
        Default is None.
    name : str, optional
        Name of the created object.
        Default is "NewObject".
    collection : bpy.types.Collection or None, optional
        Blender collection to link the object to.
        Default is None.
    uuid : str or None, optional
        Directly set the UUID on the resulting BlenderObject.
        Default is None.

    Returns
    -------
    BlenderObject
        A wrapped Blender mesh object.
    """

    bob = BlenderObject(
        create_mesh_object(
            vertices=vertices,
            edges=edges,
            faces=faces,
            name=name,
            collection=collection,
        )
    )
    if uuid:
        bob._uuid = uuid
        bob.object.uuid = uuid  # type: ignore
    return bob


# Friendly alias for BlenderObject - commonly used variable name
BOB = BlenderObject
