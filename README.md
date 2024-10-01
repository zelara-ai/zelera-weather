# Zelara Weather Worker

## Overview
Zelara Weather Worker is a microservice designed to interact with the OpenWeather API and MongoDB, retrieving and storing weather data for different cities. It uses **FastAPI** for handling API requests and Docker for deployment. The service provides functionality to add, find, and manage weather data in MongoDB.

## Prerequisites
Before running this service, ensure you have the following installed:
- **Docker**: Install Docker from [here](https://docs.docker.com/get-docker/).
- **MongoDB**: The service interacts with MongoDB as the data store.
- **OpenWeather API Key**: You will need an API key from OpenWeather. [Sign up here](https://home.openweathermap.org/users/sign_up) to get one.

## Setup and Running the Application

### 1. Clone the Repository:
```bash
git clone https://github.com/zelara-ai/zelera-weather.git>
cd zelara-weather
```

### 2. Environment Configuration:
Create a `.env` file in the root directory with your OpenWeather API key:
```
OPENWEATHER_API_KEY=your_api_key_here
MONGO_URL=mongodb://db:27017/zelara_db
```

### 3. Start the Application:
You can use Docker Compose to easily set up and run the services:
```bash
docker-compose up
```

This will start:
- **MongoDB** container.
- **FastAPI** server running the weather worker.

The application will be accessible at `http://localhost:8000`.

### 4. Accessing the API:
- **Base URL**: `http://localhost:8000/`
- **Get all data**: `GET /api/data`
- **Find city by name**: `GET /find/city?name=<city_name>`
- **Find city by ID**: `GET /find/id?id=<city_id>`
- **Add a city**: `POST /add?city=<city_name>`

## Development

### 1. Update MongoDB Fixtures:
- Modify the `db-fixtures/fixture.json` file to add initial data for the database.
- You can rebuild the container to apply the new data with:
  ```bash
  docker-compose down
  docker-compose up
  ```

### 2. Modify the FastAPI Application:
- The application logic resides in `src/main.py`. You can add more routes or modify existing functionality here.
  
### 3. Rebuild and Restart the Application:
After making changes, run:
```bash
docker-compose down
docker-compose up --build
```

### 4. Running Tests:
You can test the API locally using tools like **Postman** or **curl**. Ensure the MongoDB container is running before performing any tests.

## Deployment

### Docker Build and Push to Registry:
- The project includes a GitHub Actions workflow for automating the Docker image build and pushing it to GitHub Container Registry (GHCR).
- The workflow is triggered when you push a new tag (e.g., `v1.0.0`).
  
To deploy:
1. Tag your commit:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
2. The GitHub Action will automatically build and push the Docker image to GHCR.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
