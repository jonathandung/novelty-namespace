# ruff: file-ignore[undocumented-public-method, useless-expression]
"""Tests for novelty_namespace."""

import sys
import unittest as u

import novelty_namespace as m


class TestSubclassProhibited(u.TestCase):
    def test_cannot_subclass_meta(self):
        with self.assertRaises(TypeError):

            class Meta(m.NamespaceMeta): ...


class TestNamespaceBasics(u.TestCase):
    def test_create_namespace_via_metaclass(self):
        class NS(metaclass=m.NamespaceMeta):
            x = 1
            y = 2

        self.assertIsInstance(NS, m.Namespace)
        self.assertEqual(NS.x, 1)
        self.assertEqual(NS.y, 2)

    def test_repr(self):
        class NS(metaclass=m.NamespaceMeta): ...

        self.assertIn("NS", repr(NS))
        self.assertTrue(repr(NS).startswith("<"))
        self.assertTrue(repr(NS).endswith(">"))

    def test_attribute_errors(self):
        class NS(metaclass=m.NamespaceMeta):
            a = 1

        with self.assertRaises(AttributeError):
            NS.nonexistent
        with self.assertRaises(AttributeError):
            NS.also_missing

    def test_direct_instantiation_is_private(self):
        ns = m.Namespace("name", (), {"a": 1})
        self.assertEqual(ns.a, 1)


class TestNamespaceMutation(u.TestCase):
    def test_namespace_attributes_are_writable(self):
        class NS(metaclass=m.NamespaceMeta):
            a = 1

        NS.a = 2
        self.assertEqual(NS.a, 2)
        NS.b = 3
        self.assertEqual(NS.b, 3)
        del NS.b
        with self.assertRaises(AttributeError):
            NS.b

    def test_namespace_is_unhashable(self):
        class NS(metaclass=m.NamespaceMeta): ...

        with self.assertRaises(TypeError):
            hash(NS)


class TestInheritance(u.TestCase):
    def test_bases_are_consulted(self):
        class Base(metaclass=m.NamespaceMeta):
            inherited = "yes"

        class Derived(Base):
            own = "here"

        self.assertEqual(Derived.own, "here")
        self.assertEqual(Derived.inherited, "yes")

    def test_instance_dict_shadows_base(self):
        class Base(metaclass=m.NamespaceMeta):
            val = "base"

        class Derived(Base):
            val = "derived"

        self.assertEqual(Derived.val, "derived")

    def test_multiple_inheritance_lookup_order(self):
        class A(metaclass=m.NamespaceMeta):
            name = "A"

        class B(metaclass=m.NamespaceMeta):
            name = "B"

        class C(A, B): ...

        self.assertEqual(C.name, "A")


class TestFrozenNamespace(u.TestCase):
    def test_frozen_attributes_readable(self):
        class F(metaclass=m.FrozenNamespaceMeta):
            a = 1

        self.assertEqual(F.a, 1)

    def test_frozen_setattr_raises(self):
        class F(metaclass=m.FrozenNamespaceMeta):
            a = 1

        with self.assertRaises(m.FrozenNamespaceError):
            F.a = 2

    def test_frozen_delattr_raises(self):
        class F(metaclass=m.FrozenNamespaceMeta):
            a = 1

        with self.assertRaises(m.FrozenNamespaceError):
            del F.a

    def test_frozen_error_is_attribute_error(self):
        self.assertTrue(issubclass(m.FrozenNamespaceError, AttributeError))


class TestModuleMetaclasses(u.TestCase):
    def test_module_meta_registers_submodule(self):
        class MySub(metaclass=m.ModuleMeta):
            value = 42

        self.assertIs(sys.modules["test_novelty_namespace.MySub"], MySub)

    def test_frozen_module_meta_is_frozen(self):
        class FrozenSub(metaclass=m.FrozenModuleMeta):
            value = 1

        self.assertEqual(FrozenSub.value, 1)
        with self.assertRaises(m.FrozenNamespaceError):
            FrozenSub.value = 2

    def test_main_module_name_is_top_level(self):
        class InMain(metaclass=m.ModuleMeta):
            __module__ = "__main__"

        self.assertIn("InMain", sys.modules)
        self.assertIs(sys.modules["InMain"], InMain)


class TestMetaclassCompatibility(u.TestCase):
    def test_incompatible_metaclass_rejected(self):
        class OtherMeta(type): ...

        with self.assertRaises(TypeError):

            class Bad(metaclass=m.NamespaceMeta, **{"metaclass": OtherMeta}): ...


class TestExtractDict(u.TestCase):
    def test_copy_by_default(self):
        class NS(metaclass=m.NamespaceMeta):
            a = 1
            b = 2

        d = m.extract_dict(NS)
        self.assertEqual(d["a"], 1)
        self.assertEqual(d["b"], 2)
        d["a"] = 99
        self.assertEqual(NS.a, 1)

    def test_writethrough_returns_internal_dict(self):
        class NS(metaclass=m.NamespaceMeta):
            a = 1

        d = m.extract_dict(NS, writethrough=True)
        self.assertIs(d, m.extract_dict(NS, writethrough=True))
        d["a"] = 2
        self.assertEqual(NS.a, 2)

    def test_writethrough_on_frozen_raises(self):
        class F(metaclass=m.FrozenNamespaceMeta):
            a = 1

        with self.assertRaises(m.FrozenNamespaceError):
            m.extract_dict(F, writethrough=True)

    def test_copy_of_frozen_works(self):
        class F(metaclass=m.FrozenNamespaceMeta):
            a = 1

        d = m.extract_dict(F)
        self.assertEqual(d["a"], 1)
        if sys.version_info >= (3, 15):
            self.assertIsInstance(d, frozendict)


class TestGetName(u.TestCase):
    def test_qualified_name_includes_module(self):
        class Named(metaclass=m.NamespaceMeta): ...

        self.assertEqual(m.get_name(Named), "test_novelty_namespace.Named")
        self.assertEqual(m.get_name(Named, qualified=False), "Named")


class TestAllExport(u.TestCase):
    def test_all_names_exist(self):
        for name in m.__all__:
            self.assertTrue(hasattr(m, name), f"missing export: {name}")

    def test_private_helpers_removed(self):
        for name in (
            "a",
            "r",
            "module",
            "namespace",
            "frozennamespace",
            "frozenmodule",
            "TYPE_CHECKING",
            "annotations",
        ):
            self.assertFalse(hasattr(m, name), f"leaked private name: {name}")
