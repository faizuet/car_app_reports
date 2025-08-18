from car_tasks.celery_app import celery
import sys

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python celery_run.py [worker|beat]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == 'worker':
        celery.worker_main(['worker', '--pool=solo', '--loglevel=info'])
    elif cmd == 'beat':
        celery.start(argv=['beat', '--loglevel=info'])
    else:
        print(f"Unknown command: {cmd}")
        print("Usage: python celery_run.py [worker|beat]")
        sys.exit(1)
