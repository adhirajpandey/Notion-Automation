#Importing Libraries
from flask import Flask, render_template, redirect, url_for
import os
import subprocess
import logging

from kafka import KafkaProducer
import json

producer = KafkaProducer(bootstrap_servers="localhost:29092")
KAFKA_TOPIC = "NOTION_TASKS"

def setup_logging():
    logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


app = Flask(__name__)


@app.route("/")
def home():
    return {"message": "Hello World"}

@app.route("/ui")
def ui():
    return render_template("index.html")

@app.route("/synctasks")
def trigger_notion_tasks_sync():
    logging.info("Sync tasks route accessed.")
    data = {"task_type" : "sync_tasks"}
    producer.send(KAFKA_TOPIC, json.dumps(data).encode("utf-8"))
    print("Sync Tasks request sent to kafka topic")
    return redirect(url_for("ui"))

@app.route("/deploymentstatus")
def trigger_project_deployments_check():
    logging.info("Deployment status route accessed.")
    data = {"task_type" : "deployment_status"}
    producer.send(KAFKA_TOPIC, json.dumps(data).encode("utf-8"))
    print("Deployment Status request sent to kafka topic")
    return redirect(url_for("ui"))


if __name__ == "__main__":
    setup_logging()
    logging.info("Starting the application.")
    PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))