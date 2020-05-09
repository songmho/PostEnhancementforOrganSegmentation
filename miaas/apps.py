__author__ = 'hanter'

from miaas import container

from django.apps import AppConfig


class MedicalImageConfig(AppConfig):
    name = 'miaas'

    def ready(self):
        container.Container()
