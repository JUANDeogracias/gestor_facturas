from __future__ import absolute_import, unicode_literals

from celery import shared_task

'''
    En este archivo dejamos definidas todas las tareas compartidas para utilizarlas en otros lugares
'''

@shared_task
def ping():
    return 'pong'

@shared_task
def enviar_email():
    print(f"Enviando correo a con asunto y mensaje ")

    return True

# Dejamos una tarea compartida
@shared_task()
def sumar(a,b):
    return a+b