"""App configuration for the 'pages' app."""
from django.apps import AppConfig


class PagesConfig(AppConfig):
    """App configurations"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pages'

    def ready(self):
        """Insert Questions to the database"""
        import pages.signals # pylint: disable=import-outside-toplevel, unused-import
