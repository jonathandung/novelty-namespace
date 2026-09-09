# Copyright (c) 2026 Jonathan Dung
# All rights reserved.
"""Provides a metaclass for creating self-contained namespaces with inheritance support."""
import types
from contextlib import suppress


class NamespaceMeta(type):
    __cnt = __import__("itertools").count()

    def __new__(cls, n, b, a, /, **k):  # ruff: ignore[undocumented-public-method]
        if (c := k.pop("metaclass")) is not cls:
            x = f"NamespaceMeta is not compatible with {c}"
            raise TypeError(x)
        if (m := a.get("__module__")) is None:
            m = f"<unknown-{next(cls.__cnt)}>"
        return _Namespace(f"{m}.{n}", types.resolve_bases(b), {**a, **k})


__reg = {}

class _Namespace:
    def __init__(self, *a):
        __reg[id(self)] = a

    def __getattribute__(self, n, a=suppress(AttributeError), b=suppress(KeyError), /):
        r = __reg[id(self)]
        with b:
            return r[2][n]
        for c in r[1]:
            with a:
                return getattr(c, n)
        raise AttributeError(n)

    def __setattr__(self, n, v, /):
        __reg[id(self)][2][n] = v

    def __delattr__(self, n, /):
        del __reg[id(self)][2][n]

    def __repr__(self):
        return f"<namespace {__reg[id(self)][0]}>"

    def __del__(self):
        del __reg[id(self)]

    __hash__ = None


def extract_dict(ns, *, writethrough=False):
    """Give a dictionary representing the members of the namespace.

    Args:
        ns: The namespace to extract the dictionary from.
        writethrough: If True, the returned dictionary will be a reference to the
            internal dictionary of the namespace; otherwise, a copy of the internal
            dictionary will be returned, which is the default behaviour.

    Returns:
        A dictionary representing the members of the namespace.

    """
    d = __reg[id(ns)][2]
    return d if writethrough else d.copy()
