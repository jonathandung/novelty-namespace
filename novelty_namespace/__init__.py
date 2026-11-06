# Copyright (c) 2026 Jonathan Dung
# All rights reserved.
"""Create self-contained namespaces with inheritance support."""

from contextlib import suppress

__all__ = (
    "FrozenModuleMeta",
    "FrozenNamespaceError",
    "FrozenNamespaceMeta",
    "ModuleMeta",
    "NamespaceMeta",
    "extract_dict",
    "get_name",
)
_ = {}
"""A private mapping from memory address of namespaces to a tuple of the form
(name, bases, instance dictionary).
"""


class FrozenNamespaceError(AttributeError):
    """Raised when an attempt is made to modify an attribute on a frozen namespace."""


class Namespace:
    """The type of all namespaces or submodules created by this module."""

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


class frozen_namespace(Namespace):
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


class frozen_module(a, frozen_namespace): ...


class module(a, namespace): ...


def r(n):
    m = "cannot subclass " + n

    def _(c, /, **k):  # ruff: ignore[unused-function-argument]
        raise TypeError(m)

    return classmethod(_)


class B(type):
    def __init_subclass__(cls, r=r, _=__import__("types").resolve_bases, /, *, t):
        def z(p, n, b, a, /, **k):
            if (c := k.pop("metaclass", p)) is not p:
                x = f"{cls.__name__} is not compatible with {c.__qualname__}"
                raise TypeError(x)
            return t(
                n
                if (m := a.get("__module__")) is None or m == "__main__"
                else f"{m}.{n}",
                _(b),
                a | k,
            )

        cls.__new__, cls.__init_subclass__ = z, r(cls.__name__)


class NamespaceMeta(B, t=namespace):
    """Choose this metaclass to create a namespace using class syntax."""


class FrozenNamespaceMeta(B, t=frozen_namespace):
    """Choose this metaclass to create a frozen namespace using class syntax.

    Attributes on frozen namespaces are immutable.
    """


class ModuleMeta(B, t=module):
    """Choose this metaclass to create a submodule using class syntax.

    The submodule lives under the current module and can be imported as such, unless
    created in the __main__ module, in which case it is considered top-level.
    """


class FrozenModuleMeta(B, t=frozen_module):
    """Choose this metaclass to create a frozen submodule using class syntax.

    Attributes on frozen submodules are immutable.
    """


def extract_dict(ns: Namespace, *, writethrough: bool = False):
    """Give a dictionary representing the members of the namespace.

    Args:
      ns: The namespace to extract the dictionary from.
      writethrough:
        If True, the returned dictionary will be a reference to the
        internal dictionary of the namespace; otherwise, a copy of the internal
        dictionary will be returned, which is the default behaviour.

    Returns:
        A dictionary representing the members of the namespace.

    """
    d = _[id(ns)][2]
    return d if writethrough else d.copy()


def get_name(ns: Namespace, *, qualified: bool = True):
    """Return the name of the namespace passed.

    Args:
      ns: The namespace to get the name of.
      qualified: Whether to return the qualified name. True by default.

    Returns:
      The name of the namespace.

    """
    n = _[id(ns)][0]
    return n if qualified else n.rpartition(".")[-1]


del B, frozen_module, frozen_namespace, a, module, namespace, suppress, r
