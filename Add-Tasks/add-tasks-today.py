import logging
import os
import requests
from dotenv import load_dotenv
import datetime
import json
import pytz

load_dotenv()


NOTION_API_TOKEN = os.getenv("NOTION_API_TOKEN")
TASKS_DB_ID = os.getenv("TASKS_DB_ID")
JOURNAL_DB_ID = os.getenv("JOURNAL_DB_ID")


# get current date in YYYY-MM-DD format
def get_current_date() -> str:
    ist = pytz.timezone('Asia/Calcutta')
    current_datetime = datetime.datetime.now(ist)
    
    formatted_datetime = current_datetime.strftime('%Y-%m-%d')

    return formatted_datetime

# read notion database and return json data1
def read_notion_db(database_id: str) -> dict:
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
    
# get today's page id from journal database
def get_today_pageid_from_journal_db(journal_db: dict) -> str:
    try:
        for page in journal_db["results"]:
            if page["properties"]["Name"]["title"][0]["mention"]["date"]["start"] == get_current_date():
                return page["id"]
            else:
                return None
    except Exception as e:
        logging.error(e)

# read children blocks properties from page id       
def read_children_blocks_from_pageid(page_id: str) -> dict:
    try:
        url = f"https://api.notion.com/v1/blocks/{page_id}/children"

        payload = {}
        headers = {
        'Notion-Version': '2022-06-28',
        'Authorization': 'Bearer ' + NOTION_API_TOKEN
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        return response.json()

    except Exception as e:
        logging.error(e)

# get today's tasks block id from today's page all blocks
def get_today_tasks_blockid_from_page_blocks(blocks_data) -> str:   
    tasks_block_id = blocks_data["results"][0]["id"]

    if tasks_block_id:
        return tasks_block_id
    else:
        return None

# add task to today's journal page in today's tasks block
def add_tasks_to_today_task_page(block_id, tasks_list: list) -> int:
    try:
        headers = {
            'Authorization': f'Bearer {NOTION_API_TOKEN}',
            'Content-Type': 'application/json',
            'Notion-Version': '2022-06-28'
        }

        data = {
            "children": []
        }

        for task in tasks_list:
            task_string = task["properties"]["Name"]["title"][0]["text"]["content"]
            task_payload = {
                    "object": "block",
                    "type": "to_do",
                    "to_do": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": task_string
                                }
                            }
                        ],
                        "checked": False,
                        "color": "default"
                    }
                }
            data["children"].append(task_payload)

        url = f'https://api.notion.com/v1/blocks/{block_id}/children'
        
        response = requests.patch(url, headers=headers, json=data)

        return response.status_code
    
    except Exception as e:
        logging.error(e)

# filter tasks that are marked for pickup today and status is not done
def filter_tasks(task_db: dict, already_added_tasks: list) -> list[dict]:
    filtered_tasks = []
    
    for task in task_db["results"]:
        completion_status = task["properties"]["Status"]["status"]["name"]
        
        if completion_status == "In progress":
                task_string = task["properties"]["Name"]["title"][0]["text"]["content"]
                if task_string not in already_added_tasks:
                    filtered_tasks.append(task)
    
    return filtered_tasks

# get already added tasks from today's page
def get_added_tasks_from_today_page(today_tasks_blockid: str) -> list:
    try:
        url = f"https://api.notion.com/v1/blocks/{today_tasks_blockid}/children"

        headers = {
        'Notion-Version': '2022-06-28',
        'Authorization': 'Bearer ' + NOTION_API_TOKEN
        }

        response = requests.request("GET", url, headers=headers)

        response_data = response.json()

        added_tasks = []

        for block in response_data["results"]:
            if block["type"] == "to_do":
                added_tasks.append(block["to_do"]["rich_text"][0]["text"]["content"])

        return added_tasks

    except Exception as e:
        logging.error(e)
        return []

    
if __name__ == "__main__":

    tasks_db = read_notion_db(TASKS_DB_ID)
    journal_db = read_notion_db(JOURNAL_DB_ID)

    today_pageid = get_today_pageid_from_journal_db(journal_db)
    today_page_blocks = read_children_blocks_from_pageid(today_pageid)
    today_tasks_blockid = get_today_tasks_blockid_from_page_blocks(today_page_blocks)

    already_added_tasks = get_added_tasks_from_today_page(today_tasks_blockid)

    filtered_tasks = filter_tasks(tasks_db, already_added_tasks)

    if len(filtered_tasks) > 0:
        add_tasks_to_today_task_page(today_tasks_blockid, filtered_tasks)
        print(f"Added all the filtered tasks to today's page")
    else:
        print("No tasks to add today")

