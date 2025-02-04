from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
from django.conf import settings

# Configuracion predeterminada de django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestor_fernauro.settings')

#
app = Celery('gestor_fernauro')

# Leemos la configuración de Django y la establecemos en Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

'''
    Definimos el comando que vamos a utilizar para ejecutar el worker:
        - celery -A gestor_fernauro worker --loglevel=info --pool=solo
'''

