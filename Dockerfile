FROM python:3-alpine3.15

WORKDIR /app/Deployment-Server

COPY . /app

RUN pip install -r requirements.txt 

CMD ["sh", "start.sh"]
