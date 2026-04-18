from importlib import import_module

from django.apps import AppConfig


class TransactionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'transactions'

    def import_models(self):
        self.models_module = import_module(f'{self.name}.infrastructure.models')
        self.models = self.apps.all_models[self.label]
