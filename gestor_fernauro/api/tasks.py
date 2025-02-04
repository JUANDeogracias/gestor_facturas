from __future__ import absolute_import, unicode_literals

import os
from datetime import datetime

from celery import shared_task


@shared_task
def ping():
    return 'pong'
@shared_task
def enviar_email():
    print(f"Enviando correo a con asunto y mensaje ")

    return True

'''
    Mediante esta funcion vamos ha dejar los registros de los logs y los vamos a añadir al archivo logs.py
'''
@shared_task
def registrar_log(*args):
    # Obtener la fecha y hora actual en formato legible
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Ruta del archivo de log
    log_file_path = os.path.join(os.getcwd(), 'logs.py') # Es una funcion que permite saber el directorio actual y trabajar a partir de él

    with open(log_file_path, 'a') as log_file:
        '''
            Esto permite escribir en el archivo y dejar registrado los logs. Además el 'a' permite abrir el archivo en el
            modo appends esto significa que va a abrir el archivo y en vez de sobreescribir va a añadir al final de el
            archivo.
        '''
        log_file.write(f'# Registro de log - {current_time} \n')
        ''' 
            Esta parte la podríamos comentar pero gracias a el log anterior podemos dejar la fecha y horas de el log
            y de este modo saber lo que se ha quedado registrado en el archivo.
        '''
        for arg in args:
            log_file.write(f'{arg}\n')
        log_file.write('\n')

    print(f"Log registrado en {log_file_path}")

