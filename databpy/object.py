from uuid import uuid1

import bpy
import numpy as np
from bpy.types import Object
from mathutils import Matrix
from numpy import typing as npt

from . import attribute as attr
from .addon import register
from .attribute import (
    AttributeDomain,
    AttributeDomains,
    AttributeTypes,
    _check_obj_attributes,
    evaluate_object,
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
        self.objects = list(bpy.context.scene.objects)
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
        current_objects = bpy.context.scene.objects
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
        if obj.uuid == uuid:
            return obj

    raise LinkedObjectError(
        "Failed to find an object in the database with given uuid: " + uuid
    )


class BlenderObject:
    """
    A convenience class for working with Blender objects
    """

    def __init__(self, obj: Object | str | None = None):
        """
        Initialize the BlenderObject.

        Parameters
        ----------
        obj : Object | None
            The Blender object to wrap.
        """
        self._uuid: str = str(uuid1())
        self._object_name: str = ""

        if not hasattr(bpy.types.Object, "uuid"):
            register()

        if isinstance(obj, Object):
            if obj.uuid != "":
                self._uuid = obj.uuid
            self.object = obj
        elif isinstance(obj, str):
            obj = bpy.data.objects[obj]
            if obj.uuid != "":
                self._uuid = obj.uuid
            self.object = obj
        elif obj is None:
            self._object_name = ""

    def _check_obj(self) -> None:
        _check_obj_attributes(self.object)

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
            if obj.uuid != self.uuid:
                obj = get_from_uuid(self.uuid)
        except KeyError:
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
            value.uuid = self.uuid
        except AttributeError:
            register()
            value.uuid = self.uuid
        self._object_name = value.name

    @property
    def uuid(self) -> str:
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
        if not isinstance(self.object.data, bpy.types.Mesh):
            raise TypeError("Object must be a mesh to create a new object from pydata")
        vertices, edges, faces = [
            [] if x is None else x for x in (vertices, edges, faces)
        ]
        self.object.data.clear_geometry()
        self.object.data.from_pydata(vertices, edges, faces)
        return self.object

    def store_named_attribute(
        self,
        data: np.ndarray,
        name: str,
        atype: str | AttributeTypes | None = None,
        domain: str | AttributeDomain = AttributeDomains.POINT,
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
        return self

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

    def set_boolean(self, array: np.ndarray, name: str) -> None:
        """
        Store a boolean attribute on the Blender object.

        Parameters
        ----------
        array : np.ndarray
            The boolean data to be stored as an attribute.
        name : str
            The name for the attribute.
        """
        self.store_named_attribute(array, name=name, atype=AttributeTypes.BOOLEAN)

    def evaluate(self) -> Object:
        """
        Return a version of the object with all modifiers applied.

        Returns
        -------
        Object
            A new Object that isn't yet registered with the database
        """
        return evaluate_object(self.object)

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

    def attributes(self):
        """
        Get the attributes of the Blender object.

        Returns
        -------
        bpy.types.Attributes
            The attributes of the Blender object.
        """
        return self.object.data.attributes

    @property
    def vertices(self):
        """
        Get the vertices of the Blender object.

        Returns
        -------
        bpy.types.Vertices
            The vertices of the Blender object.
        """

        return self.object.data.vertices

    @property
    def edges(self):
        """
        Get the edges of the Blender object.

        Returns
        -------
        bpy.types.Edges
            The edges of the Blender object.
        """
        return self.object.data.edges

    def transform_origin(self, matrix: Matrix) -> None:
        """
        Transform the origin of the Blender object.

        Parameters
        ----------
        matrix : Matrix
            The transformation matrix to apply to the origin.
        """
        self.object.matrix_local = matrix * self.object.matrix_world

    def transform_points(self, matrix: Matrix) -> None:
        """
        Transform the points of the Blender object.

        Parameters
        ----------
        matrix : Matrix
            The transformation matrix to apply to the points.
        """
        self.position = self.position * matrix

    @property
    def selected(self) -> np.ndarray:
        """
        Get the selected vertices of the Blender object.

        Returns
        -------
        np.ndarray
            The selected vertices of the Blender object.
        """
        return self.named_attribute(".select_vert")

    @property
    def position(self) -> np.ndarray:
        """
        Get the position of the vertices of the Blender object.

        Returns
        -------
        np.ndarray
            The position of the vertices of the Blender object.
        """
        return self.named_attribute("position")

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

    def selected_positions(self, mask: np.ndarray | None = None) -> np.ndarray:
        """
        Get the positions of the selected vertices, optionally filtered by a mask.

        Parameters
        ----------
        mask : np.ndarray | None, optional
            The mask to filter the selected vertices. Defaults to None.

        Returns
        -------
        np.ndarray
            The positions of the selected vertices.
        """
        if mask is not None:
            return self.position[np.logical_and(self.selected, mask)]

        return self.position[self.selected]

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
        if evaluate:
            strings = list(self.evaluate().data.attributes.keys())
        else:
            strings = list(self.object.data.attributes.keys())

        if not drop_hidden:
            return strings
        else:
            return [x for x in strings if not x.startswith(".")]

    def __len__(self) -> int:
        """
        Get the number of vertices in the Blender object.

        Returns
        -------
        int
            The number of vertices in the Blender object.
        """
        return len(self.object.data.vertices)


def create_object(
    vertices: npt.ArrayLike | None = None,
    edges: npt.ArrayLike | None = None,
    faces: np.ndarray | None = None,
    name: str = "NewObject",
    collection: bpy.types.Collection | None = None,
) -> Object:
    """
    Create a new Blender object and corresponding mesh.

    Vertices are created for each row in the vertices array. If edges and / or faces are created then they are also
    initialized but default to None.

    Parameters
    ----------
        vertices : np.ndarray, optional
            The vertices of the vertices as a numpy array. Defaults to None.
        edges : np.ndarray, optional
            The edges of the object as a numpy array. Defaults to None.
        faces : np.ndarray, optional
            The faces of the object as a numpy array. Defaults to None.
        name : str, optional
            The name of the object. Defaults to 'NewObject'.
        collection : bpy.types.Collection, optional
            The collection to link the object to. Defaults to None.

    Returns
    -------
        Object
            The created object.
    """
    if vertices is None:
        vertices = []
    if edges is None:
        edges = []
    if faces is None:
        faces = []
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices=vertices, edges=edges, faces=faces)
    obj = bpy.data.objects.new(name, mesh)
    if collection is None:
        collection = create_collection("Collection")
    collection.objects.link(obj)
    return obj


def create_bob(
    vertices: np.ndarray | None = None,
    edges: np.ndarray | None = None,
    faces: np.ndarray | None = None,
    name: str = "NewObject",
    collection: bpy.types.Collection | None = None,
    uuid: str | None = None,
) -> BlenderObject:
    """
    Create a BlenderObject wrapper around a new Blender object.

    Parameters
    ----------
    vertices : ndarray or None, optional
        Array of vertex coordinates. Each row represents a vertex.
        Default is None.
    edges : ndarray or None, optional
        Array of edge indices. Each row contains indices of vertices forming an edge.
        Default is None.
    faces : ndarray or None, optional
        Array of face indices. Each row contains indices of vertices forming a face.
        Default is None.
    name : str, optional
        Name of the created object.
        Default is "NewObject".
    collection : bpy.types.Collection or None, optional
        Blender collection to link the object to.
        Default is None.
    uuid : str or None, optional
        Directly set the UUID on the resulting BlenderObject rather than generating one.
        Default is None.

    Returns
    -------
    BlenderObject
        A wrapped Blender object with additional functionality.

    See Also
    --------
    :func:`create_object` : The underlying function used to create the Blender object.

    Notes
    -----
    If uuid is provided, it will be set both on the BlenderObject wrapper
    and the underlying Blender object.

    Examples
    --------
    ```{python}
    import numpy as np
    from databpy.object import create_bob
    vertices = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]])
    bob = create_bob(vertices=vertices, name="MyObject")
    print(bob.name)
    print(len(bob))
    bob.named_attribute("position")
    ```


    """
    bob = BlenderObject(
        create_object(
            vertices=vertices,
            edges=edges,
            faces=faces,
            name=name,
            collection=collection,
        )
    )
    if uuid:
        bob._uuid = uuid
        bob.object.uuid = uuid

    return bob
