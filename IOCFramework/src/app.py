from typing import Union, Callable, Any, TypeVar, Type

Resolver = Callable[[Any, Any, str, dict], Any]

Instantiable = TypeVar("instantiable", str, Any)

class App:
    _bindings = {}
    _singletons = {}
    _custom_resolvers = {}
    _resolve_obj: Resolver = None

    def __init__(self, resolver: Resolver):
        self._resolve_obj = resolver

    def get_custom_resolver(self, class_val):
        return self._custom_resolvers.get(class_val, None)


    def add_bindings(self, bindings: dict):
        _bindings = {key: self._resolve_binding(value) for key, value in bindings.items()}
        self._bindings.update(_bindings)
    
    def get_binding(self, class_val: Instantiable):
        return self._bindings.get(class_val, None)

    def add_singletons(self, singletons: dict):
        _bindings = {key: self._resolve_singleton(value) for key, value in singletons.items()}
        self._bindings.update(_bindings)
    
    def when(self, class_val: Instantiable, needs: Instantiable, give: Union[Instantiable, Callable]):
        needs_dict = self._custom_resolvers.get(class_val, {})
        needs_dict[needs] = give
        self._custom_resolvers[class_val] = needs_dict
    
    def make(self, class_val: Instantiable):
        return self.make_with(class_val=class_val)

    def make_with(self, class_val: Instantiable, using: dict={}):
        return self._resolve_obj(class_val=class_val, using=using, app=self)

    def _resolve_binding(self, class_val: Instantiable, using={}):
        def func(using={}):
            return self._resolve_obj(class_val=class_val, using=using, app=self, is_binding=True)
        return func
        
    def _resolve_singleton(self, class_val: Instantiable, using={}):
        def func(with_val={}):
            with_val = with_val if with_val else using
            if self._singletons.__contains__(class_val):
                return self._singletons.get(class_val)
            else:
                self._singletons[class_val] = self._resolve_binding(class_val, with_val)()
                return self._singletons[class_val]
        return func