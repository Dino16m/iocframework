import unittest
from unittest import mock, TestCase
from IOCFramework import App
MockResolvedName = mock.Mock()
MockResolvedName.mock_name = "hello dummy"

class DummyDependencyInterface:
    is_interface: bool
    def __init__(self):
        self.is_interface = True

class DummyDependencyImpl(DummyDependencyInterface):
    def __init__(self):
        self.is_interface = False

class DummyClass:
    dummy_service: DummyDependencyInterface
    def __init__(self, dummy_service: DummyDependencyInterface):
        self.dummy_service = dummy_service

    def dummy_behaviour(self):
        return self.dummy_service.is_interface


class TestApp(TestCase):
    app: App
    resolve_obj: mock.Mock
    def setUp(self):
        resolve_obj = mock.Mock(side_effect=[MockResolvedName, mock.Mock(), mock.Mock()])
        self.app = App(resolve_obj)
        self.resolve_obj = resolve_obj
    
    def test_custom_resolver_resolves_annotations(self):
        self.app.when(DummyClass, DummyDependencyInterface, DummyDependencyImpl)
        custom_resolver = self.app.get_custom_resolver(DummyClass)
        implementation = custom_resolver.get(DummyDependencyInterface)
        self.assertEqual(implementation, DummyDependencyImpl)
    
    def test_custom_resolver_resolves_annotations_lambda(self):
        self.app.when(
            DummyClass, 
            DummyDependencyInterface, 
            lambda: DummyDependencyImpl
        )
        custom_resolver = self.app.get_custom_resolver(DummyClass)
        implementation = custom_resolver.get(DummyDependencyInterface)
        self.assertTrue(callable(implementation))
        self.assertEqual(implementation(), DummyDependencyImpl)

    def test_custom_resolver_resolves_param_name(self):
        dummy_service = 'dummy_service'
        self.app.when(
            DummyClass, 
            dummy_service, 
            DummyDependencyImpl
        )
        custom_resolver = self.app.get_custom_resolver(DummyClass)
        implementation = custom_resolver.get(dummy_service)
        self.assertEqual(implementation, DummyDependencyImpl)
    
    def test_get_binding(self):
        bindings = {
           DummyDependencyInterface: DummyDependencyImpl 
        }
        self.app.add_bindings(bindings)
        binding = self.app.get_binding(DummyDependencyInterface)
        self.assertTrue(callable(binding))
        implementation = binding()
        self.assertEqual(implementation, MockResolvedName)
    
    def test_get_singletons(self):
        singletons = {
           DummyDependencyInterface: DummyDependencyImpl 
        }
        self.app.add_singletons(singletons)
        first_binding = self.app.get_binding(DummyDependencyInterface)
        second_binding = self.app.get_binding(DummyDependencyInterface)
        first_implementation = first_binding()
        second_implementation = second_binding()
        self.assertEqual(first_implementation, second_implementation)
        self.assertEqual(first_implementation, MockResolvedName)
    
    def test_app_makes_instance(self):
        class_val = DummyDependencyInterface
        self.app.make(class_val)
        self.resolve_obj.assert_called_once_with(
            **{"app": self.app, "class_val": class_val, "using":{}}
        )
    
