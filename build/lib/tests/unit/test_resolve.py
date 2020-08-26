from unittest import TestCase, mock
from IOCFramework import BindingResolutionException, NameResolutionException, App
import inspect
from IOCFramework.src.resolve import (
    resolve_obj, _get_class_from_path, _get_binding, _resolve_dependency, init_class
)

class DummyClass:
    def __init__(self):
        self.name = "dummy"


class DummyClassWithArgs:
    a: DummyClass
    b: int
    def __init__(self, a: DummyClass, b: int):
        self.a = a
        self.b = b

class TestResolve(TestCase):
    app: mock.Mock
    def setUp(self):
        self.app = mock.Mock()
    
    def test_get_class_from_path(self):
        dummy_class_path = "tests.unit.test_resolve.DummyClass"
        dummy_class = _get_class_from_path(dummy_class_path)
        self.assertEqual(dummy_class, DummyClass)
    
    def test_get_binding(self):
        mock_binding = mock.Mock(return_value=DummyClass())
        self.app.get_binding.return_value = mock_binding
        binding = _get_binding(DummyClass, self.app)
        self.assertIsInstance(binding, DummyClass)
    
    def test_resolve_dependency_from_callable_custom_resolver(self):
        param = mock.Mock()
        param.name = "dummy"
        param.annotation = DummyClass
        self.app.get_custom_resolver.return_value = {param.name: lambda: DummyClass()}
        resolved = _resolve_dependency(param, DummyClass, self.app)
        self.assertIsInstance(resolved, DummyClass)

        self.app.get_custom_resolver.return_value = {param.annotation: lambda: DummyClass()}
        resolved = _resolve_dependency(param, DummyClass, self.app)
        self.assertIsInstance(resolved, DummyClass)

    def test_resolve_dependency_from_non_callable_custom_resolver(self):
        param = mock.Mock()
        param.name = "dummy"
        param.annotation = DummyClass
        self.app.get_custom_resolver.return_value = {param.name: DummyClass()}
        resolved = _resolve_dependency(param, DummyClass, self.app)
        self.assertIsInstance(resolved, DummyClass)

        self.app.get_custom_resolver.return_value = {param.annotation: DummyClass()}
        resolved = _resolve_dependency(param, DummyClass, self.app)
        self.assertIsInstance(resolved, DummyClass) 
    
    @mock.patch("IOCFramework.src.resolve._get_binding")
    def test_resolve_dependency_using_default_param(self, mocked_get_binding):
        param = mock.Mock()
        param.default = "default"
        self.app.get_custom_resolver.return_value = None
        mocked_get_binding.return_value = None
        resolved = _resolve_dependency(param, DummyClass, self.app)
        self.assertEqual(resolved, param.default)
    
    @mock.patch("IOCFramework.src.resolve._get_binding")
    def test_resolve_dependency_using_binding(self, mocked_get_binding):
        param = mock.Mock()
        param.default = "default"
        self.app.get_custom_resolver.return_value = None
        mocked_get_binding.return_value = "not default"
        resolved = _resolve_dependency(param, DummyClass, self.app)
        self.assertEqual(resolved, mocked_get_binding.return_value)
    
    @mock.patch("IOCFramework.src.resolve._get_binding")
    def test_resolve_dependency_using_callable_binding(self, mocked_get_binding):
        param = mock.Mock()
        param.default = "default"
        self.app.get_custom_resolver.return_value = None
        mocked_get_binding.return_value = lambda: "not default"
        resolved = _resolve_dependency(param, DummyClass, self.app)
        self.assertEqual(resolved, mocked_get_binding.return_value())
    
    @mock.patch("IOCFramework.src.resolve._get_binding")
    def test_resolve_dependency_raises_exception_when_unresolvable(self, mocked_get_binding):
        param = mock.Mock()
        param.default = inspect._empty
        param.annotation = inspect._empty
        self.app.get_custom_resolver.return_value = None
        mocked_get_binding.return_value = None
        with self.assertRaises(BindingResolutionException):    
            _resolve_dependency(param, DummyClass, self.app)
    
    @mock.patch("IOCFramework.src.resolve._resolve_dependency")
    def test_init_class_with_args(self, mocked_resolve_dependency: mock.MagicMock):
        using = {'a': DummyClass()}
        mocked_resolve_dependency.return_value = 20
        params = inspect.signature(DummyClassWithArgs.__init__).parameters.values()
        class_instance = init_class(DummyClassWithArgs, self.app, params, using)
        self.assertIsInstance(class_instance, DummyClassWithArgs)
        self.assertEqual(class_instance.a, using['a'])
        self.assertEqual(class_instance.b,  mocked_resolve_dependency.return_value)
    
    def test_init_class_without_args(self):
        class_instance = init_class(DummyClass, self.app, {})
        self.assertIsInstance(class_instance, DummyClass)

    @mock.patch("IOCFramework.src.resolve.init_class")    
    def test_resolve_object_from_string(self, mocked_init_class: mock.MagicMock):
        class_name = "tests.unit.test_resolve.DummyClass"
        resolved_obj = resolve_obj(self.app, class_name, {}, True)
        mocked_init_class.assert_called()
    
    @mock.patch("IOCFramework.src.resolve.init_class")    
    def test_resolve_object_raises_exception_if_path_not_found(self, mocked_init_class: mock.MagicMock):
        wrong_class_name = "tests.unit.test_resolve.DummyCinta"
        with self.assertRaises(NameResolutionException):
            resolve_obj(self.app, wrong_class_name, {})
    


