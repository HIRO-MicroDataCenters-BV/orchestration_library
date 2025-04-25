# Orchestration Library

## Overview

This project contains a FastAPI-based backend and a PostgreSQL database container that initializes with tables on startup using SQL scripts.

## Run the project

```bash
docker-compose up --build
```
- PostgreSQL will initialize with init.sql only once on first run.
- FastAPI runs on http://localhost:8000
- Swagger documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs)

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

curl -X POST http://localhost:8000/workload-request-decisions/ \
  -H "Content-Type: application/json" \
  -d '{
    "workload_request_id": 1,
    "node_name": "node-1",
    "queue_name": "main-queue",
    "status": "pending"
}'
```

