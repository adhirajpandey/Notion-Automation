#Importing Libraries
from flask import Flask, render_template, redirect, url_for
import os
import subprocess


PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


app = Flask(__name__)

@app.route("/")
def home():
    return {"message": "Hello World"}

@app.route("/ui")
def ui():
    return render_template("index.html")

@app.route("/synctasks")
def trigger_notion_tasks_sync():
    subprocess.run(["python", f"{PROJECT_DIR}/Add-Tasks/add-tasks-today.py"])
    return redirect(url_for("ui"))

@app.route("/deploymentstatus")
def trigger_project_deployments_check():
    subprocess.run(["python", f"{PROJECT_DIR}/Deployments-Status/tracker.py"])
    return redirect(url_for("ui"))


app.run(host='0.0.0.0', port=5000)