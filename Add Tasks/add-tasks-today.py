import logging
import os
import requests
from dotenv import load_dotenv
from datetime import date
import json

load_dotenv()


NOTION_API_TOKEN = os.getenv("NOTION_API_TOKEN")
TASKS_DB_ID = os.getenv("TASKS_DB_ID")
JOURNAL_DB_ID = os.getenv("JOURNAL_DB_ID")


# get current date in YYYY-MM-DD format
def get_current_date() -> str:
    return str(date.today())

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
    for page in journal_db["results"]:
        if page["properties"]["Name"]["title"][0]["mention"]["date"]["start"] == get_current_date():
            return page["id"]
        else:
            return None

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
def add_task_to_today_task_page(block_id, task_string: str) -> int:
    try:
        url = f'https://api.notion.com/v1/blocks/{block_id}/children'
        
        headers = {
            'Authorization': f'Bearer {NOTION_API_TOKEN}',
            'Content-Type': 'application/json',
            'Notion-Version': '2022-06-28'
        }

        data = {
            "children": [
                {
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
            ]
        }

        response = requests.patch(url, headers=headers, json=data)

        return response.status_code
    
    except Exception as e:
        logging.error(e)

# filter tasks that are marked for pickup today and status is not done
def filter_tasks(task_db: dict) -> list[dict]:
    filtered_tasks = []
    
    for task in task_db["results"]:
        completion_status = task["properties"]["Status"]["status"]["name"]
        
        if completion_status == "Not started":
            pickup_status = task["properties"]["Pickup"]["select"]["name"]
            
            if pickup_status == "1":
                filtered_tasks.append(task)
    
    return filtered_tasks


if __name__ == "__main__":

    tasks_db = read_notion_db(TASKS_DB_ID)
    journal_db = read_notion_db(JOURNAL_DB_ID)

    today_pageid = get_today_pageid_from_journal_db(journal_db)
    today_page_blocks = read_children_blocks_from_pageid(today_pageid)
    today_tasks_blockid = get_today_tasks_blockid_from_page_blocks(today_page_blocks)

    filtered_tasks = filter_tasks(tasks_db)

    if len(filtered_tasks) > 0:
        for task in filtered_tasks:
            task_string = task["properties"]["Name"]["title"][0]["text"]["content"]
            add_task_to_today_task_page(today_tasks_blockid, task_string)
            print(f"Added task: {task_string}")
    else:
        print("No tasks to add today")

