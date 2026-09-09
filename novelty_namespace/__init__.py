import contextlib
import types


class NamespaceMeta(type):
    __cnt = __import__("itertools").count()

    def __new__(cls, n, b, a, /, **k):
        if (c := k.pop("metaclass")) is not cls:
            x = f"NamespaceMeta is not compatible with {c}"
            raise TypeError(x)
        if (m := a.get("__module__")) is None:
            m = f"<unknown-{next(cls.__cnt)}>"
        return Namespace(f"{m}.{n}", types.resolve_bases(b), {**a, **k})


__reg = {}

class Namespace:
    def __init__(self, *a):
        __reg[id(self)] = a

    def __getattribute__(self, n, _=contextlib.suppress(AttributeError), /):
        r = __reg[id(self)]
        try:
            return r[2][n]
        except KeyError:
            ...
        for b in r[1]:
            with _:
                return getattr(b, n)
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
    d = __reg[id(ns)][2]
    return d if writethrough else d.copy()
