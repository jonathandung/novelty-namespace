# Copyright (c) 2026 Jonathan Dung
# All rights reserved.
"""Create self-contained namespaces with inheritance support."""

from contextlib import suppress

__all__ = (
    "FrozenModuleMeta",
    "FrozenNamespaceError",
    "FrozenNamespaceMeta",
    "ModuleMeta",
    "Namespace",
    "NamespaceMeta",
    "NamespaceMetaBase",
    "extract_dict",
    "get_name",
)
_ = {}
"""A mapping from memory address of namespaces to their attributes and metadata."""
TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Any
__version__ = "0.4.0"


class FrozenNamespaceError(AttributeError):
    """Raised when an attempt is made to modify an attribute on a frozen namespace."""


class Namespace:
    """The type of all namespaces or submodules created by this module.

    .. note::
      When using class syntax to subclass a namespace, do not specify any metaclass;
      otherwise, you will get a :class:`TypeError`.
    """

    def __init__(self, *a):
        """Initialize the namespace. Private; should never be called."""
        _[id(self)] = a

    def __getattribute__(self, n, a=suppress(AttributeError), b=suppress(KeyError), /):
        r = _[id(self)]
        with b:
            return r[2][n]
        for c in r[1]:
            with a:
                return getattr(c, n)
        raise AttributeError(n)

    def __repr__(self):
        n = _[id(self)][0]
        return f"<{type(self).__name__} {n}>"

    def __del__(self):
        if _ is not None:  # ty: ignore[redundant-condition-strict]
            _.pop(id(self), None)


class frozennamespace(Namespace):
    def __setattr__(*_):
        raise FrozenNamespaceError

    __delattr__ = __setattr__


class namespace(Namespace):
    def __setattr__(self, n, v, /):
        _[id(self)][2][n] = v

    def __delattr__(self, n, /):
        del _[id(self)][2][n]

    __hash__ = None


class a(Namespace):
    def __init__(self, *a, _=__import__(name="sys").modules):
        """Initialize the module."""
        super().__init__(*a)
        _[a[0]] = self  # ty: ignore[invalid-assignment]


class frozenmodule(a, frozennamespace): ...


class module(a, namespace): ...


def r(n):

    def _(c, m="cannot subclass " + n, /, **k):  # ruff: ignore[unused-function-argument]
        raise TypeError(m)

    return classmethod(_)


class NamespaceMetaBase(type):
    """Base class for metaclasses used to create namespaces."""

    def __init_subclass__(
        cls,
        r=r,
        f=__import__("types").resolve_bases,
        u=lambda a, b, _=__import__("itertools").chain: frozendict(
            _(a.items(), b.items())
        ),
        /,
        *,
        t,
    ):
        def z(_, n, b, a, /, **k):
            return t(
                n
                if (m := a.get("__module__")) is None or m == "__main__"
                else f"{m}.{n}",
                f(b),
                a | k if t.__hash__ is None else u(a, k),
            )

        cls.__new__, cls.__init_subclass__ = z, r(cls.__name__)


class NamespaceMeta(NamespaceMetaBase, t=namespace):
    """Choose this metaclass to create a namespace using class syntax."""


class FrozenNamespaceMeta(NamespaceMetaBase, t=frozennamespace):
    """Choose this metaclass to create a frozen namespace using class syntax.

    Attributes on frozen namespaces are immutable.
    """


class ModuleMeta(NamespaceMetaBase, t=module):
    """Choose this metaclass to create a submodule using class syntax.

    The submodule lives under the current module and can be imported as such, unless
    created in the ``__main__`` module, in which case it is considered top-level.
    """


class FrozenModuleMeta(NamespaceMetaBase, t=frozenmodule):
    """Choose this metaclass to create a frozen submodule using class syntax.

    Attributes on frozen submodules are immutable.
    """


def extract_dict(
    ns: Namespace, *, writethrough: bool = False
) -> dict[str, Any] | frozendict[str, Any]:
    """Give a dictionary representing the members of the namespace.

    Args:
      ns: The namespace to extract the dictionary from.
      writethrough:
        ``False`` by default. If ``True``, the returned dictionary will be a reference
        to the internal dictionary of the namespace; otherwise, a copy of the internal
        dictionary will be returned.

    Returns:
        A possibly frozen dictionary representing the members of the namespace.

    Raises:
        FrozenNamespaceError:
          When ``writethrough=True`` is specified and ns is a frozen namespace, the
          attributes of which are not writeable by design.

    """
    d = _[id(ns)][2]
    if not writethrough:
        return d.copy()
    if object.__getattribute__(ns, "__hash__") is None:  # ruff: ignore[unnecessary-dunder-call]
        return d
    raise FrozenNamespaceError


def get_name(ns: Namespace, *, qualified: bool = True) -> str:
    """Return the name of the namespace passed.

    Args:
      ns: The namespace to get the name of.
      qualified:
        Whether to return the qualified name (i.e. including the module where it was
        defined). ``True`` by default.

    Returns:
      The name as a string.

    """
    n = _[id(ns)][0]
    return n if qualified else n.rpartition(".")[-1]  # ty: ignore[unsound-return]


del TYPE_CHECKING, frozenmodule, frozennamespace, a, module, namespace, suppress, r
