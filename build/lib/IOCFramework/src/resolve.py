import inspect
from typing import Any, Union
import importlib
from unittest import mock
from .app import App, Instantiable
from ..exceptions import BindingResolutionException, NameResolutionException


def _is_not_primitive(val: Any):
    try:
        inspect.signature(val)
    except ValueError:
        return False
    return True

def _get_class_from_path(python_path: str):
    try:
        seperator_pos = python_path.rfind('.')
        module_path = python_path[:seperator_pos]
        class_name = python_path[seperator_pos + 1:]
        return getattr(importlib.import_module(module_path), class_name)
    except Exception:
        return None

def _get_binding(annotation: Any, app: App, using={}):
    binding = app.get_binding(annotation)
    return binding(using) if binding else None

def  _resolve_dependency(param: inspect.Parameter, class_obj: Instantiable , app: App):
    """
        Try to get the instance of a parameter from a bound custom resolver for the class which needs it.
        if not able to do the above, try to get a registered binding for the parameter's Annotation.
        if no binding is registered for the Annotation, get the default value of the parameter
        if the default value is empty, try to instantiate the param's Annnotation class
    """
    class_context = app.get_custom_resolver(class_obj)
    custom_resolver = (class_context.get(param.name) 
                    or class_context.get(param.annotation)) if class_context else None
    resolved = custom_resolver() if callable(custom_resolver) else custom_resolver
    if resolved:
        return resolved
    default = param.default
    binding = _get_binding(param.annotation, app) or default
    if binding == inspect._empty:
        if param.annotation != inspect._empty and _is_not_primitive(param.annotation):
            annotation_params = _get_init_params(param.annotation)
            binding = init_class(param.annotation, app, annotation_params)
        else:
            raise BindingResolutionException(
                f'Cannot resolve param {param.name} of class {class_obj}'
            )
    return binding() if callable(binding) else binding
 
def init_from_binding(class_obj: Instantiable, app: App, using={}, is_binding=False):
    """
        Get binding for a class 
        as registered in the app's singleton or regular binding mappings
    """
    if not is_binding:
        binding = _get_binding(class_obj, app, using)
        if binding:
            return binding
    return None

def init_class(class_obj: Instantiable, app: App, params: list, using={}):
    constructor_args = []
    for param in params:
        name = param.name
        special_args = ("self", "*args", "args", "**kwargs", "kwargs")
        if name in special_args:
            continue
        value = using.get(name) if using.__contains__(name) else  _resolve_dependency(param, class_obj, app)
        constructor_args.append(value)
    return class_obj(*(constructor_args))

def  _get_init_params(class_obj: Instantiable):
    is_func = inspect.isfunction(class_obj)
    sig = inspect.signature(class_obj) if is_func else inspect.signature(class_obj.__init__)
    return sig.parameters.values()

def resolve_obj(app: App, class_val: Instantiable, using={}, is_binding=False):
    class_obj = _get_class_from_path(class_val) if type(class_val) == str else class_val
    if not class_obj:
        raise NameResolutionException(f'{class_val} does not exist')
    params =  _get_init_params(class_obj)
    if is_binding:
        class_instance = init_class(class_obj, app, params, using)
    else:
        class_instance = init_from_binding(class_obj, app, using, is_binding) or init_class(class_obj, app, params, using)
    return class_instance
