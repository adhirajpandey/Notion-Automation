from kafka import KafkaConsumer
import json
import subprocess
import os

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KAFKA_TOPIC = "NOTION_TASKS"

consumer = KafkaConsumer(
    KAFKA_TOPIC, 
    bootstrap_servers="kafka:29092"
)

print("Now consuming")

while True:
    "Consuming......"
    for message in consumer:
        consumed_message = json.loads(message.value.decode())
        print(consumed_message)
        if consumed_message["task_type"] == "sync_tasks":
            print("EXECUTING SYNC TASKS SCRIPT")
            subprocess.run(["python", f"{PROJECT_DIR}/Add-Tasks/add-tasks-today.py"])
        elif consumed_message["task_type"] == "deployment_status":
            print("EXECUTING DEPLOYMENT STATUS SCRIPT")
            subprocess.run(["python", f"{PROJECT_DIR}/Deployments-Status/tracker.py"])
        else:
            print("INVALID DATA")