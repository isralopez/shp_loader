import os

__version__ = (0, 1, 0, 'alpha', 0)


class ShpLoaderException(Exception):
    """Base class for exceptions in this module."""
    pass


def get_version():
    import shp_loader.version
    return shp_loader.version.get_version(__version__)


def main(global_settings, **settings):
    from django.core.wsgi import get_wsgi_application
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings.get('django_settings'))
    app = get_wsgi_application()
    return app