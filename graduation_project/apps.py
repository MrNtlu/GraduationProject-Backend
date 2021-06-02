from django.apps import AppConfig

class GraduationProjectConfig(AppConfig):
    name = 'graduation_project'
    
    def ready(self):
        from .schedule import classifier
        classifier.start()