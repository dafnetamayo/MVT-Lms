from django.apps import AppConfig
import mimetypes
mimetypes.add_type("text/javascript", ".js", True)
mimetypes.add_type("text/css", ".css", True)


class LmsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'lms'

    def ready(self):
        import lms.signals
