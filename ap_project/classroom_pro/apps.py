from django.apps import AppConfig


class ClassroomProConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'classroom_pro'

    def ready(self):
        import classroom_pro.signals
