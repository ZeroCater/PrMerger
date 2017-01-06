release: python manage.py migrate
web: gunicorn prmerger.wsgi --log-file - --reload
worker: python manage.py rqworker
