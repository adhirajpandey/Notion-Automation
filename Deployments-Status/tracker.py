import requests
import json
import time
import os
from datetime import datetime
import pytz
import logging
from dotenv import load_dotenv

load_dotenv()

NOTION_API_TOKEN = os.getenv("NOTION_API_TOKEN")
DEPLOYMENT_DB_ID = os.getenv("DEPLOYMENT_DB_ID")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")


def get_current_datetime() -> str:
    ist = pytz.timezone('Asia/Calcutta')
    current_datetime = datetime.now(ist)

    formatted_datetime = current_datetime.strftime('%d-%m-%Y %H:%M:%S')

    return formatted_datetime


def set_logging_config():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s:%(levelname)s:%(message)s',
                        handlers=[
                            logging.FileHandler('deployment-tracker.log', encoding='utf-8'),
                            logging.StreamHandler()
                        ])


def read_notion_deployments_database(database_id: str) -> dict:
    try:
        headers = {
            "Authorization": "Bearer " + NOTION_API_TOKEN,
            "Content-Type": "application/json",
            "Notion-Version": "2022-02-22"
        }

        api_url = f"https://api.notion.com/v1/databases/{database_id}/query"
        res = requests.request("POST", api_url, headers=headers)

        response_data = res.json()

        return response_data

    except Exception as e:
        logging.error(e)


def extract_data_from_notion_response(response_data: dict) -> list[dict]:
    results = response_data["results"]

    extracted_data = []

    for result in results:
        properties = result["properties"]
        extracted_data.append({
            "name": properties["Project Name"]["title"][0]["plain_text"],
            "status": properties["Label"]["status"]["name"],
            "link": properties["Link"]["rich_text"][0]["plain_text"],
            "notion_page_id": get_pageid_from_notion_url(result["url"]),
        })

    return extracted_data


def check_project_deployment_status(project_link: str, max_retries: int = 5, timeout: int = 5) -> str:
    try:
        for i in range(max_retries):
            response = requests.get(project_link, allow_redirects=True, timeout=timeout)
            if response.status_code == 200:
                return "Healthy"
            else:
                time.sleep(2)
        return "Down"

    except Exception as e:
        logging.error(e)
        return "Down"


def get_pageid_from_notion_url(notion_url: str) -> str:
    return notion_url.split("-")[-1]


def update_status_in_project_page(page_id: str, new_status: str) -> int:
    try:
        headers = {
            "Authorization": "Bearer " + NOTION_API_TOKEN,
            "Content-Type": "application/json",
            "Notion-Version": "2022-02-22"
        }

        update_data_payload = {
            "properties": {
                "Label": {
                    "status": {
                        "name": new_status
                    }
                }
            }
        }

        api_url = f"https://api.notion.com/v1/pages/{page_id}"

        response = requests.request("PATCH", api_url, headers=headers, data=json.dumps(update_data_payload))

        return response.status_code

    except Exception as e:
        logging.error(e)
        return -1


def check_deployment_status_and_update(deployment_data: list[dict]) -> list[dict]:
    for project in deployment_data:
        try:
            latest_status = check_project_deployment_status(project_link=project["link"])
            project["latest_status"] = latest_status

            if project["latest_status"] != project["status"]:
                update_status_in_project_page(project["notion_page_id"], latest_status)
                logging.info(f"Updated {project['name']} from {project['status']} to {latest_status}")
            else:
                logging.info(f"No Change in {project['name']}")
        except Exception as e:
            logging.error(e)

    return deployment_data


def get_discord_message_payload(deployment_status_data: list[dict]) -> str:
    payload = ""
    payload += f"Checked at: {get_current_datetime()}\n\n"

    for entry in deployment_status_data:
        if entry["latest_status"] == "Healthy":
            payload += f"{entry['name']}: ✅\n"
        else:
            payload += f"{entry['name']}: ❌\n"

    return payload


def send_message_to_discord(username: str, message: str) -> int:
    try:
        headers = {
            "Content-Type": "application/json"
        }
        payload = {
            "content": message,
            "username": username,
        }

        response = requests.post(url=DISCORD_WEBHOOK_URL, data=json.dumps(payload), headers=headers)

        return response.status_code

    except Exception as e:
        logging.error(e)
        return -1


if __name__ == "__main__":
    try:
        set_logging_config()

        # Getting Deployment DB Data
        deployment_db_raw_data = read_notion_deployments_database(DEPLOYMENT_DB_ID)
        deployment_db_data = extract_data_from_notion_response(deployment_db_raw_data)
        logging.info(f"Deployment DB Data: {deployment_db_data}")

        # Checking Deployment Health Status and Updating Notion DB
        deployment_statuses = check_deployment_status_and_update(deployment_db_data)
        logging.info(f"Deployment Statuses: {deployment_statuses}")

        # Send Status Report/Alert to Discord
        message_payload = get_discord_message_payload(deployment_statuses)
        send_message_to_discord("Deployments Tracker", message_payload)
        logging.info(f"Message Payload: {message_payload}")

    except Exception as e:
        logging.error(e)
        ERROR_MESSAGE = f"Error occurred while checking deployments at {get_current_datetime()}\n\n{e}"
        send_message_to_discord("Deployment Monitoring Alert", ERROR_MESSAGE)