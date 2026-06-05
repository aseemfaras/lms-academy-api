from django.apps import AppConfig


class TrainersConfig(AppConfig):
    name = 'trainers'

    def ready(self):
        import trainers.signals
