# Copyright (c) 2026 Jonathan Dung
# All rights reserved.
"""Create self-contained namespaces with inheritance support."""

import sys
from contextlib import suppress
from types import resolve_bases

_reg = {}
"""A private mapping from memory address of namespaces to a tuple of the form
(name, bases, instance dictionary).
"""
_lock = __import__("_thread").RLock()
"""The re-entrant mutex used to protect dictionary accesses."""


class Namespace:
    def __init__(self, *a):
        """Initialize the namespace. Private; should never be called."""
        with _lock:
            _reg[id(self)] = a

    def __getattribute__(self, n, a=suppress(AttributeError), b=suppress(KeyError), /):
        with _lock:
            r = _reg[id(self)]
        with b:
            return r[2][n]
        for c in r[1]:
            with a:
                return getattr(c, n)
        raise AttributeError(n)

    def __setattr__(self, n, v, /):
        with _lock:
            _reg[id(self)][2][n] = v

    def __delattr__(self, n, /):
        with _lock:
            del _reg[id(self)][2][n]

    def __repr__(self):
        with _lock:
            n = _reg[id(self)][0]
        return f"<namespace {n}>"

    def __del__(self):
        if _reg is not None:  # ty: ignore[redundant-condition-strict]
            with _lock:
                _reg.pop(id(self), None)

    __hash__ = None


class Module(Namespace):
    def __init__(self, *a):
        """Initialize the module."""
        super().__init__(*a)
        with _lock:
            sys.modules[a[0]] = self  # ty: ignore[invalid-assignment]


class NamespaceMeta(type):
    """Choose this metaclass to create a namespace using class syntax."""

    __cnt = __import__("itertools").count()

    def __new__(cls, n, b, a, t=Namespace, /, **k):  # ruff: ignore[undocumented-public-method]
        if (c := k.pop("metaclass", cls)) is not cls:
            x = f"NamespaceMeta is not compatible with {c.__qualname__}"
            raise TypeError(x)
        if (m := a.get("__module__")) is None:
            m = f"<anon#{next(cls.__cnt)}>"
        return t(n if m == "__main__" else f"{m}.{n}", resolve_bases(b), {**a, **k})


class ModuleMeta(NamespaceMeta):
    """Choose this metaclass to create a submodule using class syntax.

    The submodule lives under the current module and can be imported as such, unless
    created in the __main__ module.
    """

    def __new__(cls, n, b, a, t=Module, /, **k):
        """Construct the submodule."""
        return super().__new__(cls, n, b, a, t, **k)


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
    with _lock:
        d = _reg[id(ns)][2]
    return d if writethrough else d.copy()


def get_name(ns: Namespace, *, qualified: bool = True):
    """Return the name of the namespace passed.

    Args:
      ns: The namespace to get the name of.
      qualified: Whether to return the qualified name. True by default.

    Returns:
      The name of the namespace.

    """
    with _lock:
        n = _reg[id(ns)][0]
    return n if qualified else n.rpartition(".")[-1]


del Module, Namespace, suppress
