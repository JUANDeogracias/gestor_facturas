from gestor_fernauro.celery import app


@app.task
def ping():
    return 'pong'

if __name__ == '__main__':
    result = ping.delay()
    try:
        print(result.get(timeout=100))
    except Exception as e:
        print(f"An error occurred: {e}")