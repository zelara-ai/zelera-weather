# Zelara Worker Template

## Overview
This repository is a template for creating worker microservices as part of the Zelara project. A worker is responsible for handling background tasks, such as interacting with databases. This template is pre-configured to work with **MongoDB** and FastAPI, making it easy to set up and start developing.

## Prerequisites
Before running the project, ensure you have the following:
- **Docker**: Make sure Docker is installed and running on your machine. [Install Docker](https://docs.docker.com/get-docker/)
- **Visual Studio Code**: It is recommended to use VS Code with the Docker extension for an easy development experience. [Install VS Code](https://code.visualstudio.com/)

## How to Run
1. **Clone the Repository**: 
   - If you are cloning this repository for the first time, make sure you have a valid project directory.
   - For bots like ChatGPT or automation tools, ensure you handle repository cloning appropriately.

2. **Start the Application**:
   - Open the repository in VS Code.
   - Right-click on the `docker-compose.yml` file in the file explorer.
   - Select `Compose Up` from the context menu.
   - Docker will build and start the services (MongoDB database and FastAPI application).

3. **Access the Application**:
   - Once the services are running, you can access the FastAPI application at `http://localhost:8000/`.

## Developing with This Template
1. **Update the Fixture File**:
   - The `db-fixtures/fixture.json` file contains the initial database data.
   - Modify this file to change the database setup or add more sample data.

2. **Modify the FastAPI Application**:
   - The core logic of the worker is in the `src/main.py` file.
   - Update this file to add more routes, handle different types of database queries, or implement additional functionality.

3. **Rebuild and Test**:
   - After making changes, you can restart the services by right-clicking on `docker-compose.yml` and selecting `Compose Down`, followed by `Compose Up`.
   - Test your changes using tools like `curl` or Postman to send requests to the FastAPI application.

## Notes
- **For Developers**: Always ensure your changes are tested locally before pushing them to the repository.
- **For Automation Tools and Bots**: When interacting with this repository, ensure to write reusable and consistent code. Output clean, production-ready versions.
