#Importing Libraries
from flask import Flask, render_template, redirect, url_for
import os
import subprocess
import logging


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
    subprocess.run(["python", f"{PROJECT_DIR}/Add-Tasks/add-tasks-today.py"])
    return redirect(url_for("ui"))

@app.route("/deploymentstatus")
def trigger_project_deployments_check():
    logging.info("Deployment status route accessed.")
    subprocess.run(["python", f"{PROJECT_DIR}/Deployments-Status/tracker.py"])
    return redirect(url_for("ui"))


if __name__ == "__main__":
    setup_logging()
    logging.info("Starting the application.")
    PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    app.run(host='0.0.0.0', port=5000)