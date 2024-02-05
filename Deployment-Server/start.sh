nohup python3 consumer.py >> consumernohup.out 2>&1 &

gunicorn --bind 0.0.0.0:5002 wsgi:app