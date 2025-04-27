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

### Workload Requests
- `POST /workload-requests/`

### Workload Request Decisions
- `POST /workload-request-decisions/`
- `GET /workload-request-decisions/` - Retrieve workload request decisions based on filters.
- `GET /workload-request-decisions/{workload_request_id}` - Retrieve a specific workload request decision by ID.
- `PUT /workload-request-decisions/{workload_request_id}` - Update a workload request decision by ID.
- `DELETE /workload-request-decisions/{workload_request_id}` - Delete a workload request decision by ID.

## Example Requests

### Create a Workload Request
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
```

### Create a Workload Request Decision
```bash
curl -X POST http://localhost:8000/workload-request-decisions/ \
  -H "Content-Type: application/json" \
  -d '{
    "workload_request_id": 1,
    "node_name": "node-1",
    "queue_name": "main-queue",
    "status": "pending"
}'
```

### Retrieve Workload Request Decisions with Filters
```bash
curl -X GET "http://localhost:8000/workload-request-decisions/?node_name=node-1&status=pending" \
  -H "accept: application/json"
```

### Retrieve a Specific Workload Request Decision
```bash
curl -X GET "http://localhost:8000/workload-request-decisions/1" \
  -H "accept: application/json"
```

### Update a Workload Request Decision
```bash
curl -X PUT "http://localhost:8000/workload-request-decisions/1" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "used"
}'
```

### Delete a Workload Request Decision
```bash
curl -X DELETE "http://localhost:8000/workload-request-decisions/1" \
  -H "accept: application/json"
```