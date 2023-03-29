from django.apps import AppConfig


class WhatisthisConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'whatisthis'

def ready(self):
        import whatisthis.signals