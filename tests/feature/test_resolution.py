from unittest import TestCase, mock
from IOCFramework import get_app, App

class DummyClass:
    def __init__(self):
        pass

class DummySecondInterface:
    pass

class DummyFirstInterface:
    pass

class DummySecondDependency:
    dummy_service: DummyClass
    def __init__(self, dummy_service: DummyClass):
        self.dummy_service = dummy_service

class DummyFirstDependency:
    dummy_service: DummyClass
    def __init__(self, dummy_service: DummyClass):
        self.dummy_service = dummy_service

class DummyClassWithArgs:
    first_dep: DummyFirstInterface
    second_dep: DummySecondInterface
    def __init__(
        self, first_dep: DummyFirstInterface, 
        second_dep: DummySecondInterface
    ):
        self.first_dep = first_dep
        self.second_dep = second_dep

class TestResolution(TestCase):
    app: App
    def setUp(self):
        self.app = get_app()
    
    def test_resolves_singleton(self):
        singletons = {
            DummyClass: DummyClass
        }
        self.app.add_singletons(singletons)
        first_dep: DummyFirstDependency = self.app.make(DummyFirstDependency)
        second_dep: DummySecondDependency = self.app.make(DummySecondDependency)
        self.assertIsInstance(first_dep, DummyFirstDependency)
        self.assertIsInstance(second_dep, DummySecondDependency)
        self.assertEqual(second_dep.dummy_service, first_dep.dummy_service)
    
    def test_resolves_binding(self):
        bindings = {
            DummySecondInterface: DummySecondDependency,
            DummyFirstInterface: DummyFirstDependency,
        }
        self.app.add_bindings(bindings)
        dummy: DummyClassWithArgs = self.app.make(DummyClassWithArgs)
        self.assertIsInstance(dummy.second_dep, DummySecondDependency)
        self.assertIsInstance(dummy.first_dep, DummyFirstDependency)
    
    def test_resolves_unregistered_noargs_dependency(self):
        dummy: DummyClassWithArgs = self.app.make(DummyClassWithArgs)
        self.assertIsInstance(dummy.second_dep, DummySecondDependency)
        self.assertIsInstance(dummy.first_dep, DummyFirstDependency)
        self.assertIsInstance(dummy.second_dep.dummy_service, DummyClass)
        self.assertIsInstance(dummy.first_dep.dummy_service, DummyClass)
