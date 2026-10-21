import itertools
import warnings
from collections.abc import Iterable, Sequence
from typing import cast
from uuid import uuid1

import bpy
import numpy as np
from bpy.types import Object
from numpy import typing as npt

from . import attribute as attr
from ._deprecation import REMOVAL_VERSION
from .addon import (
    find_by_session_uid,
    get_uuid,
    session_token,
    set_uuid,
)
from .array import AttributeArray
from .attribute import (
    Attribute,
    AttributeDomains,
    AttributeTypeNames,
    AttributeTypes,
    DomainNames,
    _as_typed_attribute,
    _check_obj_attributes,
    evaluate_object,
    list_attributes,
)
from .collection import create_collection
from .errors import LinkedObjectError
from .utils import active_scene


class ObjectDatabase:
    """Typed access to `bpy.data.objects` by name, available as `databpy.object.bdo`."""

    def __getitem__(self, key: str) -> Object:
        """
        Get an object from `bpy.data.objects` by its name.

        Parameters
        ----------
        key : str
            The name of the object to get.

        Returns
        -------
        Object
            The object from `bpy.data.objects`.

        Raises
        ------
        KeyError
            If no object has the given name.
        """
        return bpy.data.objects[key]


bdo = ObjectDatabase()


class ObjectTracker:
    """
    A context manager for finding objects added to the active scene.

    Entering the context records the objects in the active scene. Objects added to the
    scene afterwards are returned by `new_objects()` and `latest()`, including after
    the context has exited.

    Methods
    -------
    new_objects()
        Return the objects added to the active scene since entering the context.
    latest()
        Return the most recently added object.
    """

    def __enter__(self):
        """
        Record the objects currently in the active scene.

        Returns
        -------
        self
            The instance of the class.
        """
        self.objects = list(active_scene().objects)
        self._existing = {obj.session_uid for obj in self.objects}
        return self

    def __exit__(self, type, value, traceback):
        pass

    def new_objects(self):
        """
        Find the objects added to the active scene since entering the context.

        Returns
        -------
        list[Object]
            The new objects, ordered from oldest to newest.
        """
        # session_uid values increase as data-blocks are created, so they give both
        # a rename-proof identity and the creation order
        new_objects = [
            obj
            for obj in active_scene().objects
            if obj.session_uid not in self._existing
        ]
        return sorted(new_objects, key=lambda obj: obj.session_uid)

    def latest(self):
        """
        Get the object most recently added to the active scene since entering the context.

        Returns
        -------
        Object
            The most recently added object.

        Raises
        ------
        IndexError
            If no objects have been added.
        """
        return self.new_objects()[-1]


def get_from_uuid(uuid: str, name_hint: str | None = None) -> Object:
    """
    Get an object from `bpy.data.objects` by the UUID databpy stored on it.

    Parameters
    ----------
    uuid : str
        The UUID of the object to get.
    name_hint : str | None, optional
        Preferred object name if several objects share the UUID, which happens when
        an object has been duplicated.

    Returns
    -------
    Object
        The object from `bpy.data.objects`.

    Raises
    ------
    LinkedObjectError
        If no object has the UUID.
    """
    matches = [obj for obj in bpy.data.objects if get_uuid(obj) == uuid]
    if not matches:
        raise LinkedObjectError(
            "Failed to find an object in the database with given uuid: " + uuid
        )
    for obj in matches:
        if obj.name == name_hint:
            return obj
    return matches[0]


class BlenderObjectBase:
    """
    Minimal base class for Blender objects with name and object access.

    Tracks an object in Blender's database and gives access to the object and its name.
    A direct reference to an object can raise `ReferenceError`, as Blender can
    reallocate data-blocks without warning, so the object is tracked in two ways:

    - Within a session, by the object's `session_uid`, which stays the same across
      renames and internal reallocations. Duplicates of the object get a new
      `session_uid`, so they are never mistaken for the original. If the object is
      removed, accessing it raises a `LinkedObjectError`.
    - Across sessions (after loading a .blend file, or in a new Python process), by a
      persistent `uuid` stored on the object as a custom property. On first access in
      a new session the object is found by its `uuid` and then tracked by its new
      `session_uid`.

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
            The Blender object to wrap, or the name of an object in `bpy.data.objects`.
            If the object already has a databpy UUID, it is reused. With None, no object
            is linked and accessing `object` raises a `LinkedObjectError`.

        Raises
        ------
        KeyError
            If `obj` is a name that no object has.
        """
        self._uuid: str = str(uuid1())
        self._object_name: str = ""
        self._session_uid: int | None = None
        self._session_token: str | None = None

        if isinstance(obj, str):
            obj = bpy.data.objects[obj]

        if isinstance(obj, Object):
            existing_uuid = get_uuid(obj)
            if existing_uuid:
                self._uuid = existing_uuid
            self.object = obj

    def _link(self, obj: Object) -> None:
        self._object_name = obj.name
        self._session_uid = obj.session_uid
        self._session_token = session_token()

    @property
    def object(self) -> Object:
        """
        Get the Blender object.

        Returns
        -------
        Object
            The Blender object.

        Raises
        ------
        LinkedObjectError
            If the object has been removed, another wrapper has stored its own UUID on
            the object, or no object has this wrapper's UUID after a file was loaded.
        """

        if self._session_token == session_token():
            obj = (
                None
                if self._session_uid is None
                else find_by_session_uid(self._session_uid, self._object_name)
            )
            if obj is None:
                raise LinkedObjectError(
                    f"The object '{self._object_name}' linked to this "
                    f"{type(self).__name__} has been removed."
                )
            # another wrapper has taken over the object by storing its own uuid on it
            if get_uuid(obj) != self.uuid:
                raise LinkedObjectError(
                    f"The object '{obj.name}' linked to this {type(self).__name__} is "
                    "now linked to a different uuid."
                )
        else:
            # new session (file loaded or new process), session_uid values are no longer
            # valid so find the object again by its persistent uuid
            obj = get_from_uuid(self.uuid, name_hint=self._object_name)

        if obj.name != self._object_name or self._session_token != session_token():
            self._link(obj)
        return obj

    @object.setter
    def object(self, value: Object) -> None:
        """
        Set the Blender object, storing this wrapper's UUID on it.

        Parameters
        ----------
        value : Object
            The Blender object to set.

        Raises
        ------
        TypeError
            If `value` is not a `bpy.types.Object`.
        """

        if not isinstance(value, Object):
            raise TypeError(f"{value} must be a bpy.types.Object")

        set_uuid(value, self.uuid)
        self._link(value)

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
        The attributes collection of the object's data-block.
    """

    def store_named_attribute(
        self,
        data: np.ndarray,
        name: str,
        atype: AttributeTypeNames | AttributeTypes | None = None,
        domain: DomainNames | AttributeDomains | None = None,
    ) -> bpy.types.Attribute:
        """
        Store a named attribute on the Blender object.

        Parameters
        ----------
        data : np.ndarray
            The data to be stored as an attribute.
        name : str
            The name for the attribute. An existing attribute with this name is
            overwritten, keeping its type and domain.
        atype : str or AttributeTypes or None, optional
            The attribute type to store the data as. Either string or selection from the
            AttributeTypes enum. None uses the type of an existing attribute, otherwise
            infers the attribute type from the input array.
        domain : str or AttributeDomains or None, optional
            The domain to store the attribute on. None uses the domain of an existing
            attribute, otherwise AttributeDomains.POINT.

        Returns
        -------
        bpy.types.Attribute
            The added or modified attribute.

        Raises
        ------
        TypeError
            If the object's data is not a Mesh, Curves or PointCloud.
        ValueError
            If `atype` or `domain` isn't a valid name, no type can be inferred, or
            `atype` is FLOAT4 before Blender 5.2.
        NamedAttributeError
            If the data length doesn't match the domain size, or `atype` or `domain`
            conflict with an existing attribute.
        AttributeMismatchError
            If the values can't be represented by the attribute's type.
        """
        self._check_obj()
        return attr.store_named_attribute(
            self.object, data=data, name=name, atype=atype, domain=domain
        )

    def remove_named_attribute(self, name: str) -> None:
        """
        Remove a named attribute from the object.

        Parameters
        ----------
        name : str
            The name of the attribute to remove.

        Raises
        ------
        AttributeNotFoundError
            If the attribute doesn't exist.
        NamedAttributeError
            If the attribute is required by Blender (e.g. `position`) and can't be
            removed.
        """
        self._check_obj()
        attr.remove_named_attribute(self.object, name=name)

    def named_attribute(self, name: str, evaluate: bool = False) -> np.ndarray:
        """
        Read a named attribute from the object as a numpy array.

        Parameters
        ----------
        name : str
            Name of the attribute to get.
        evaluate : bool, optional
            Whether to evaluate the object's modifiers before reading the attribute.
            Defaults to False.

        Returns
        -------
        np.ndarray
            A copy of the attribute's values, which doesn't sync back to Blender.

        Raises
        ------
        AttributeNotFoundError
            If the attribute doesn't exist.
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
            The data-block of the object.
        """
        return self.object.data

    @property
    def attributes(self):
        """
        Get the attributes of the Blender object.

        Returns
        -------
        bpy.types.AttributeGroupMesh | bpy.types.AttributeGroupCurves | bpy.types.AttributeGroupPointCloud
            The attributes collection of the object's data-block.
        """
        return self.data.attributes

    @property
    def position(self) -> AttributeArray:
        """
        Get the positions of the object's vertices or points.

        Returns
        -------
        AttributeArray
            A numpy array subclass that writes changed values back to Blender.

        Examples
        --------
        ```
        pos = bob.position
        pos[0] = [1, 2, 3]  # set the position of the first vertex
        pos[:, 2] = 5.0  # set every Z coordinate to 5.0
        ```
        """
        return AttributeArray(self.object, "position")

    @position.setter
    def position(self, value: np.ndarray) -> None:
        """
        Set the positions of the object's vertices or points.

        Parameters
        ----------
        value : np.ndarray
            The positions, with shape (N, 3) for the N vertices or points.
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
        List the names of the object's attributes.

        Parameters
        ----------
        evaluate : bool, optional
            Whether to first evaluate the modifiers on the object before listing the
            available attributes. Defaults to False.
        drop_hidden : bool, optional
            Whether to drop hidden attributes (those starting with a dot). Defaults to False.

        Returns
        -------
        list[str]
            The attribute names.
        """
        return list_attributes(self.object, evaluate=evaluate, drop_hidden=drop_hidden)

    def __len__(self) -> int:
        """
        Get the number of points in the Blender object.

        This is the number of vertices of a mesh, points of a point cloud, or control
        points of a Curves object.

        Returns
        -------
        int
            The number of points in the Blender object.

        Raises
        ------
        TypeError
            If the object's data is not a Mesh, Curves or PointCloud, including the
            legacy Curve type.
        """
        if isinstance(self.data, bpy.types.Mesh):
            return len(self.data.vertices)
        elif isinstance(self.data, bpy.types.PointCloud):
            return len(self.data.points)
        elif isinstance(self.data, bpy.types.Curves):
            if "position" in self.data.attributes:
                return len(self.data.attributes["position"].data)
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
            An AttributeArray with the attribute's values, which writes changed values
            back to Blender.

        Raises
        ------
        TypeError
            If name is not a string.
        AttributeNotFoundError
            If the attribute doesn't exist. This is also a KeyError.
        """
        if not isinstance(name, str):
            raise TypeError("Attribute name must be a string")
        return AttributeArray(self.object, name)

    def __setitem__(self, name: str, data: np.ndarray) -> None:
        """
        Set a named attribute using dictionary-style syntax.

        An existing attribute keeps its type and domain. A new attribute is stored on
        the POINT domain, with its type inferred from the data.

        Parameters
        ----------
        name : str
            The name of the attribute to set.
        data : np.ndarray
            The data to store in the attribute.

        Raises
        ------
        ValueError
            If no type can be inferred from the data for a new attribute.
        NamedAttributeError
            If the data length doesn't match the domain size.
        AttributeMismatchError
            If the values can't be represented by the attribute's type.
        """
        if name in self.list_attributes():
            att = Attribute(self.attributes[name])
            self.store_named_attribute(
                data=data, name=name, domain=att.domain, atype=att.atype
            )
        else:
            self.store_named_attribute(data=data, name=name)

    def _check_obj(self) -> None:
        _check_obj_attributes(self.object)

    def evaluate(self) -> Object:
        """
        Return the evaluated version of the object, with all modifiers applied.

        Returns
        -------
        Object
            The evaluated object from the dependency graph, which isn't stored in
            `bpy.data.objects`.
        """
        return evaluate_object(self.object)


class BlenderObject(BlenderObjectAttribute):
    """
    A convenience class for working with Blender objects.

    Extends BlenderObjectAttribute with methods for creating objects and calculating
    centroids.
    """

    @classmethod
    def from_mesh(
        cls,
        vertices: npt.ArrayLike | None = None,
        edges: npt.ArrayLike | None = None,
        faces: npt.ArrayLike | None = None,
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
            Vertex indices of each edge, with shape (M, 2).
            Default is None.
        faces : ndarray or None, optional
            Vertex indices of each face. Faces with different numbers of vertices can be
            given as a list of lists.
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

        Raises
        ------
        ValueError
            If `vertices` doesn't have the shape (N, 3), an edge doesn't have exactly 2
            vertex indices, or an index is outside of the vertices.
        TypeError
            If edge or face indices aren't integers.

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
        positions: npt.ArrayLike | None = None,
        curve_sizes: list[int] | npt.ArrayLike | None = None,
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

        Raises
        ------
        ValueError
            If only one of `positions` and `curve_sizes` is given, or their lengths
            don't match.

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
        positions: npt.ArrayLike | None = None,
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
        Replace the geometry of the object's mesh with vertex, edge and face data.

        Parameters
        ----------
        vertices : np.ndarray or None, optional
            Vertex coordinates with shape (N, 3).
        edges : np.ndarray or None, optional
            Vertex indices of each edge, with shape (M, 2).
        faces : np.ndarray or None, optional
            Vertex indices of each face. Faces with different numbers of vertices can be
            given as a list of lists.

        Returns
        -------
        Object
            The object, with its mesh's geometry replaced.

        Raises
        ------
        TypeError
            If the object is not a mesh, or edge or face indices aren't integers.
        ValueError
            If `vertices` doesn't have the shape (N, 3), an edge doesn't have exactly 2
            vertex indices, or an index is outside of the vertices.
        """
        if not isinstance(self.data, bpy.types.Mesh):
            raise TypeError(
                f"Object must be a mesh to create a new object from pydata, not {type(self.data)}"
            )
        arrays = _mesh_arrays(vertices, edges, faces)
        self.data.clear_geometry()
        _fill_mesh(self.data, *arrays)
        return self.object

    def centroid(self, weight: str | np.ndarray | None = None) -> np.ndarray:
        """
        Calculate the weighted or unweighted centroid of the object's positions.

        Parameters
        ----------
        weight : str | np.ndarray | None, optional
            The weights or indices for calculating the centroid. Defaults to None.

            - str: the name of an attribute, whose values are used as below
            - float array: a weight for each position
            - int array: the indices of the positions to include
            - bool array: a mask of the positions to include
            - None: all positions, weighted equally

        Returns
        -------
        np.ndarray
            The centroid position, with shape (3,).

        Raises
        ------
        TypeError
            If `weight` isn't float, integer or boolean.
        AttributeNotFoundError
            If `weight` is the name of an attribute that doesn't exist.
        """
        if isinstance(weight, str):
            weight = self.named_attribute(weight)

        if weight is None:
            return np.average(self.position, axis=0)

        weight = np.asarray(weight)
        if weight.dtype.kind == "f":
            return np.average(self.position, weights=weight, axis=0)
        elif weight.dtype.kind in "iub":
            return np.average(self.position[weight], axis=0)

        raise TypeError(
            f"`weight` must contain float weights, integer indices or a boolean mask, "
            f"not {weight.dtype}"
        )

    @property
    def vertices(self):
        """
        Get the vertices of the Blender mesh object.

        .. deprecated:: 0.5.0
            This property is mesh-specific and will be removed in databpy 0.14.0.
            Use ``bob.data.vertices`` directly for mesh objects, or use
            the attribute system (``bob['position']`` or ``bob.named_attribute('position')``)
            which works across all geometry types.

        Returns
        -------
        bpy.types.Vertices
            The vertices of the mesh object.

        Raises
        ------
        TypeError
            If the object is not a mesh.
        """
        warnings.warn(
            "BlenderObject.vertices is deprecated and will be removed in databpy "
            f"{REMOVAL_VERSION}. Use bob.data.vertices for mesh objects, or "
            "bob['position'] for geometry-agnostic attribute access.",
            FutureWarning,
            stacklevel=2,
        )
        if not isinstance(self.data, bpy.types.Mesh):
            raise TypeError(
                f"vertices property only works with Mesh objects, "
                f"not {type(self.data).__name__}"
            )
        return self.data.vertices

    @property
    def edges(self):
        """
        Get the edges of the Blender mesh object.

        .. deprecated:: 0.5.0
            This property is mesh-specific and will be removed in databpy 0.14.0.
            Use ``bob.data.edges`` directly for mesh objects.

        Returns
        -------
        bpy.types.Edges
            The edges of the mesh object.

        Raises
        ------
        TypeError
            If the object is not a mesh.
        """
        warnings.warn(
            "BlenderObject.edges is deprecated and will be removed in databpy "
            f"{REMOVAL_VERSION}. Use bob.data.edges directly for mesh objects.",
            FutureWarning,
            stacklevel=2,
        )
        if not isinstance(self.data, bpy.types.Mesh):
            raise TypeError(
                f"edges property only works with Mesh objects, "
                f"not {type(self.data).__name__}"
            )
        return self.data.edges


def _flatten_indices(
    indices: npt.ArrayLike, n_vertices: int, kind: str
) -> tuple[np.ndarray, np.ndarray]:
    """
    Flatten edge or face indices, which can have mixed sizes.

    Returns the flat vertex indices and the number of vertices in each edge or face.
    Indices outside of the vertices raise, as they would leave an invalid mesh.
    """
    try:
        array = np.asarray(indices)
    except ValueError:
        # faces with mixed sizes can't be stored as a single array
        array = None

    if array is not None and array.ndim == 2:
        flat = array.ravel()
        sizes = np.full(len(array), array.shape[1], dtype=np.int32)
    else:
        items = list(cast(Iterable[Sequence[int]], indices))
        sizes = np.fromiter(map(len, items), dtype=np.int32, count=len(items))
        flat = np.fromiter(
            itertools.chain.from_iterable(items), dtype=np.int64, count=sizes.sum()
        )

    if flat.size and flat.dtype.kind not in "iu":
        raise TypeError(f"`{kind}` must contain integer indices, not {flat.dtype}")
    if flat.size and (flat.min() < 0 or flat.max() >= n_vertices):
        raise ValueError(
            f"`{kind}` reference vertex indices outside of the {n_vertices} vertices "
            f"(found range [{flat.min()}, {flat.max()}])"
        )
    return flat.astype(np.int32, copy=False), sizes


def _mesh_arrays(
    vertices: npt.ArrayLike | None,
    edges: npt.ArrayLike | None,
    faces: npt.ArrayLike | None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Validate mesh data and convert it to the flat arrays used by `_fill_mesh`.

    Returns the vertex positions, edge vertex indices, face corner vertex indices and
    the size of each face.
    """
    vertices = np.asarray([] if vertices is None else vertices, dtype=np.float32)
    if not vertices.size:
        vertices = vertices.reshape(0, 3)
    if vertices.ndim != 2 or vertices.shape[1] != 3:
        raise ValueError(f"`vertices` must have the shape (N, 3), not {vertices.shape}")
    edge_verts, edge_sizes = _flatten_indices(
        [] if edges is None else edges, len(vertices), "edges"
    )
    if np.any(edge_sizes != 2):
        raise ValueError("`edges` must each contain exactly 2 vertex indices")
    corner_verts, face_sizes = _flatten_indices(
        [] if faces is None else faces, len(vertices), "faces"
    )
    return vertices, edge_verts, corner_verts, face_sizes


def _fill_mesh(
    mesh: bpy.types.Mesh,
    vertices: np.ndarray,
    edge_verts: np.ndarray,
    corner_verts: np.ndarray,
    face_sizes: np.ndarray,
) -> None:
    """
    Add vertices, edges and faces to an empty mesh, from the arrays of `_mesh_arrays`.

    Gives the same mesh as `mesh.from_pydata(vertices, edges, faces)`, but writes the
    data directly to the mesh's attributes from numpy arrays rather than going through
    Python tuples.
    """
    n_edges = len(edge_verts) // 2
    mesh.vertices.add(len(vertices))
    mesh.edges.add(n_edges)
    mesh.loops.add(len(corner_verts))
    mesh.polygons.add(len(face_sizes))

    if len(vertices):
        _as_typed_attribute(mesh.attributes["position"]).data.foreach_set(
            "vector", vertices.ravel()
        )
    if n_edges:
        _as_typed_attribute(mesh.attributes[".edge_verts"]).data.foreach_set(
            "value", edge_verts
        )
    if len(face_sizes):
        loop_starts = np.zeros(len(face_sizes), dtype=np.int32)
        np.cumsum(face_sizes[:-1], out=loop_starts[1:])
        mesh.polygons.foreach_set("loop_start", loop_starts)
        _as_typed_attribute(mesh.attributes[".corner_vert"]).data.foreach_set(
            "value", corner_verts
        )

    # match from_pydata, which marks faces as flat shaded. Writing the attribute
    # directly is faster than `mesh.shade_flat()`
    sharp_face = mesh.attributes.get("sharp_face") or mesh.attributes.new(
        "sharp_face", "BOOLEAN", "FACE"
    )
    _as_typed_attribute(sharp_face).data.foreach_set(
        "value", np.ones(len(face_sizes), dtype=bool)
    )

    if n_edges or len(face_sizes):
        # calculate the edges of the faces, and flag any loose edges
        mesh.update(calc_edges=bool(len(face_sizes)), calc_edges_loose=bool(n_edges))


def create_mesh_object(
    vertices: npt.ArrayLike | None = None,
    edges: npt.ArrayLike | None = None,
    faces: npt.ArrayLike | None = None,
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
        Vertex indices of each edge, with shape (M, 2). Defaults to None.
    faces : np.ndarray, optional
        Vertex indices of each face. Faces with different numbers of vertices can be
        given as a list of lists. Defaults to None.
    name : str, optional
        The name of the object. Defaults to 'Mesh'.
    collection : bpy.types.Collection, optional
        The collection to link the object to. Defaults to None, which links it to a
        collection named "Collection", created if needed.

    Returns
    -------
    Object
        The created mesh object.

    Raises
    ------
    ValueError
        If `vertices` doesn't have the shape (N, 3), an edge doesn't have exactly 2
        vertex indices, or an index is outside of the vertices.
    TypeError
        If edge or face indices aren't integers.
    """

    arrays = _mesh_arrays(vertices, edges, faces)
    mesh = bpy.data.meshes.new(name)
    _fill_mesh(mesh, *arrays)
    obj = bpy.data.objects.new(name, mesh)
    if collection is None:
        collection = create_collection("Collection")
    collection.objects.link(obj)
    return obj


def create_curves_object(
    positions: npt.ArrayLike | None = None,
    curve_sizes: list[int] | npt.ArrayLike | None = None,
    name: str = "Curves",
    collection: bpy.types.Collection | None = None,
) -> Object:
    """
    Create a new Blender Curves object (the hair curves type, not the legacy Curve type).

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
        The collection to link the object to. Defaults to None, which links it to a
        collection named "Collection", created if needed.

    Returns
    -------
    Object
        The created curves object.

    Raises
    ------
    ValueError
        If only one of positions and curve_sizes is given, or their lengths don't
        match.

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
    if (positions is None) != (curve_sizes is None):
        raise ValueError(
            "`positions` and `curve_sizes` must be given together, or both be None"
        )

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
    positions: npt.ArrayLike | None = None,
    name: str = "PointCloud",
    collection: bpy.types.Collection | None = None,
) -> Object:
    """
    Create a new Blender point cloud object.

    Parameters
    ----------
    positions : np.ndarray, optional
        The point positions as a numpy array with shape (N, 3).
        If None, creates an empty point cloud object. Defaults to None.
    name : str, optional
        The name of the object. Defaults to 'PointCloud'.
    collection : bpy.types.Collection, optional
        The collection to link the object to. Defaults to None, which links it to a
        collection named "Collection", created if needed.

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
    """
    pointcloud = bpy.data.pointclouds.new(name)
    obj = bpy.data.objects.new(name, pointcloud)

    if collection is None:
        collection = create_collection("Collection")
    collection.objects.link(obj)

    if positions is not None:
        positions = np.asarray(positions)
        pointcloud.resize(len(positions))
        attr.store_named_attribute(obj, positions, "position")

    return obj


def create_object(
    vertices: npt.ArrayLike | None = None,
    edges: npt.ArrayLike | None = None,
    faces: npt.ArrayLike | None = None,
    name: str = "NewObject",
    collection: bpy.types.Collection | None = None,
) -> Object:
    """
    Create a new Blender mesh object.

    The same as `create_mesh_object()`, with a default name of 'NewObject'.

    Parameters
    ----------
    vertices : np.ndarray, optional
        The vertices as a numpy array with shape (N, 3). Defaults to None.
    edges : np.ndarray, optional
        Vertex indices of each edge, with shape (M, 2). Defaults to None.
    faces : np.ndarray, optional
        Vertex indices of each face. Defaults to None.
    name : str, optional
        The name of the object. Defaults to 'NewObject'.
    collection : bpy.types.Collection, optional
        The collection to link the object to. Defaults to None, which links it to a
        collection named "Collection", created if needed.

    Returns
    -------
    Object
        The created mesh object.

    Raises
    ------
    ValueError
        If `vertices` doesn't have the shape (N, 3), an edge doesn't have exactly 2
        vertex indices, or an index is outside of the vertices.
    TypeError
        If edge or face indices aren't integers.
    """
    return create_mesh_object(vertices, edges, faces, name, collection)


def create_bob(
    vertices: npt.ArrayLike | None = None,
    edges: npt.ArrayLike | None = None,
    faces: npt.ArrayLike | None = None,
    name: str = "NewObject",
    collection: bpy.types.Collection | None = None,
    uuid: str | None = None,
) -> BlenderObject:
    """
    Create a BlenderObject wrapper around a new Blender mesh object.

    Parameters
    ----------
    vertices : ndarray or None, optional
        Array of vertex coordinates with shape (N, 3).
        Default is None.
    edges : ndarray or None, optional
        Vertex indices of each edge, with shape (M, 2).
        Default is None.
    faces : ndarray or None, optional
        Vertex indices of each face.
        Default is None.
    name : str, optional
        Name of the created object.
        Default is "NewObject".
    collection : bpy.types.Collection or None, optional
        Blender collection to link the object to. None links it to a collection
        named "Collection", created if needed.
        Default is None.
    uuid : str or None, optional
        The UUID to store on the object and use for the BlenderObject. None
        generates a new UUID.
        Default is None.

    Returns
    -------
    BlenderObject
        A wrapped Blender mesh object.

    Raises
    ------
    ValueError
        If `vertices` doesn't have the shape (N, 3), an edge doesn't have exactly 2
        vertex indices, or an index is outside of the vertices.
    TypeError
        If edge or face indices aren't integers.
    """

    obj = create_mesh_object(
        vertices=vertices,
        edges=edges,
        faces=faces,
        name=name,
        collection=collection,
    )
    if uuid:
        set_uuid(obj, uuid)
    return BlenderObject(obj)


# short alias for BlenderObject
BOB = BlenderObject
