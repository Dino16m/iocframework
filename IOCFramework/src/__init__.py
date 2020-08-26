from .app import App
from .resolve import resolve_obj

def get_app(resolver=resolve_obj):
    return App(resolver)