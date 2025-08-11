from tasks.celery_app import celery

if __name__ == '__main__':
   celery.start(argv=['beat', '--loglevel=info'])
