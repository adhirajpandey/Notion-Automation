# Notion-Automation

## Overview

The Notion-Automation repository comprises various automation scripts designed to enhance the functionality of Notion by providing multiple customization/personalization options for your workspace.

Each sub-directory within the repository contains scripts tailored for specific use cases, with the exception of Deployment-Server. The Deployment-Server is a Flask server designed to externally trigger these scripts.

## Features

- **Add-Tasks:** Seamlessly incorporate ongoing tasks from the central tasks Notion database into today's journal page for easy tracking and organization.
- **Deployments-Status:** Retrieve and assess the status of all deployments from the project deployments page and update them incase of any changes.
- **Simple UI:** Utilizes Notion Embed Web Page feature to integrate these scripts inside any notion page/workspace.
- **Containerized:** Availabilty of Dockerfile for easy deployments in self-hosting environment ensuring privacy over your data.


## Installation and Usage

1. Clone the project to your local system using: `git clone https://github.com/adhirajpandey/Notion-Automation`.
2. Rename `.env.example` to `.env` and update the environement variables in script's sub-directories.
3. Build docker image by running this command: `docker build -t notion_automation .` in project directory.
4. Run the container using `docker run -d -p 5000:5000 notion_automation`.
5. Embed the Hosted Flask UI in Notion page/workspace.

🔴NOTE : Please ensure that your notion databases and pages follows the same format/template as given in the demonstration, or make suitable changes in the script to facilitate your use case.

