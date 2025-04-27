# Orchestration Library

## Overview

This project contains a FastAPI-based backend and a PostgreSQL database container that initializes with tables on startup using SQL scripts.

## Run the project

```bash
docker compose up --build -d
```
- PostgreSQL will initialize with init.sql only once on first run.
- FastAPI runs on http://localhost:8000
- Swagger documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs)

To stop the containers, use the following command:

```bash
docker-compose down
```

**Note:** Using the `docker-compose down -v` option will delete the persistent volume of the database, causing all database changes to be lost. When you run `docker-compose up` again, it will create a new database with new tables. If you want to preserve the database, use `docker-compose down` without the `-v` option.


## Endpoints

- `POST /workload-requests/`
- `POST /workload-request-decisions/`

## Example Requests

```bash
curl -X POST http://localhost:8000/workload-requests/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "nginx-deployment",
    "namespace": "default",
    "api_version": "apps/v1",
    "kind": "Deployment",
    "current_scale": 3
}'

curl -X POST http://localhost:8000/workload-request-decision/ \
  -H "Content-Type: application/json" \
  -d '{
    "workload_request_id": 1,
    "node_name": "node-1",
    "queue_name": "main-queue",
    "status": "pending"
}'
```

