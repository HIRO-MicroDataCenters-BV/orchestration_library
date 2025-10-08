# Orchestration Library

## Overview

This project contains a FastAPI-based backend and a PostgreSQL database container that initializes with tables on startup using SQL scripts.

## Project Directory Structure

```
orchestration_library/
├── alembic/                        # Alembic migration configuration and migration scripts
│   ├── env.py                      # Alembic environment setup (model imports, DB URL, etc.)
│   ├── script.py.mako              # Alembic migration script template
│   └── versions/                   # Auto-generated migration files (one per schema change)
├── app/                            # Main FastAPI application source code
│   ├── __init__.py                 # Marks the directory as a Python package
│   ├── main.py                     # FastAPI app entry point
│   ├── api/                        # API route definitions (FastAPI routers)
│   ├── db/                         # Database connection and session management
│   ├── logger/                     # Logging for entire app
│   ├── metrics/                    # Custome metrics collection
│   ├── models/                     # SQLAlchemy ORM models
│   ├── repositories/               # Data access logic (CRUD operations)
│   ├── schemas/                    # Pydantic models for request/response validation
│   ├── tests/                      # Unit and integration tests
│   └── utils/                      # Utility/helper functions
├── charts/                         # Helm charts for Kubernetes deployments
│   ├── k8s-dashboard/              # Helm chart for deploying the Kubernetes Dashboard with proxy
│   │   ├── Chart.yaml              # Chart metadata and dependencies
│   │   ├── values.yaml             # Default configuration values for the chart
│   │   ├── templates/              # Kubernetes manifest templates for the dashboard
│   │   └── charts/                 # Subcharts (dependencies) if any
│   └── orchestration-api/          # Helm chart for deploying the orchestration API
│       ├── Chart.yaml              # Chart metadata and dependencies
│       ├── values.yaml             # Default configuration values for the chart
│       └── templates/              # Kubernetes manifest templates for the API
├── scripts/                        # Shell scripts for setup, deployment, and DB migrations
│   ├── create_kind_cluster.sh      # Script to create a local kind Kubernetes cluster
│   ├── deploy_orchestration_api.sh # Script to build and deploy the API to kind
│   ├── manage_db_migrations.sh     # Script to manage Alembic DB migrations
│   ├── insert_dummy_data.sh        # Script to insert dummy data(It uses dummy_data.sql file)
│   └── dummy_data.sql              # SQL commands to insert dummy data
├── Dockerfile                      # Docker build instructions for the FastAPI app
├── docker-compose.yml              # Docker Compose setup for local development (app + DB)
├── README.md                       # Project documentation and usage instructions
└── requirements.txt                # Python dependencies for the project
```

## Prerequisites

Before you begin, ensure you have the following tools installed on your system:

- [**Helm**](https://helm.sh/docs/intro/install/): Kubernetes package manager for deploying and managing charts.
- [**kubectl**](https://kubernetes.io/docs/tasks/tools/): Command-line tool for interacting with Kubernetes clusters.
- [**Docker**](https://docs.docker.com/get-docker/): Containerization platform for building and running containers.
- [**Docker Compose**](https://docs.docker.com/compose/install/): Tool for defining and running multi-container Docker applications.
- [**kind**](https://kind.sigs.k8s.io/docs/user/quick-start/#installation): Tool for running local Kubernetes clusters using Docker containers as nodes.

## Run the project

### Running on a local with docker
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

### Running on a local kind cluster

To get started with a local [kind](https://kind.sigs.k8s.io/) Kubernetes cluster and deploy the application:

1. **Initialize the kind cluster**

   Run the following script to create a kind cluster with a single node.  
   By default, the cluster will be named `kind-sample`.  
   If you provide a parameter, that will be used as the cluster name.

   ```bash
   bash scripts/create_kind_cluster.sh             # Uses default cluster name 'kind-sample'
   bash scripts/create_kind_cluster.sh my-cluster  # Uses 'my-cluster' as the cluster name
   ```

2. **Build and deploy the application**

   Use the following script to build and deploy the application inside the kind cluster.  
   If you specified a custom cluster name above, pass the same parameter here.

   ```bash
   bash scripts/deploy_orchestration_api.sh                    # Deploys to 'kind-sample' by default
   bash scripts/deploy_orchestration_api.sh my-cluster         # Deploys to 'my-cluster'
   ```

   If you do not provide any parameter, the application will be deployed to the `kind-sample` cluster.

3. **Port forward the application**

   The application runs on port `8000` inside the kind cluster.  
   To access it from your local machine, use the following port-forward command:

   ```bash
   kubectl port-forward svc/orchestration-api 28000:8000 -n orchestration-api
   ```

   Now you can access the application locally at:  
   [http://localhost:28000](http://localhost:28000) 

   Similarly, to access the PostgreSQL database running on port `5432` inside the cluster from your local machine, use:

   ```bash
   kubectl port-forward service/postgres -n orchestration-api 25432:5432
   ```
   The PostgreSQL database service will then be accessible at `localhost:25432`.

Sure! Here's the entire section fully formatted in Markdown — ready for one-click copy:

## Database Schema Changes

Follow these steps to modify the database schema using Alembic:

### 1. Modify or Add Models

   Update or add new models in the following directory:

   ```
   app/models/
   ```

   > **Note:** Stay in the project root directory when performing the following steps.

### 2. Generate Alembic Migration

   #### Script Usage
   ```bash
   bash scripts/manage_db_migrations.sh [DB_PORT] [CONTEXT] [KUBECONFIG] [NAMESPACE] [SERVICE_NAME] [--local]
   ```

   - `DB_PORT`       (default: `5432`)
   - `CONTEXT`       (default: `kind-sample`)
   - `KUBECONFIG`    (default: `~/.kube/config`)
   - `NAMESPACE`     (default: `aces-orchestration-api`)
   - `SERVICE_NAME`  (default: `aces-postgres`)
   - `--local`       (use for Docker setup)

   #### Upgrade Before Creating Migration
   
   Ensure your local database is up to date:
   
   Assuming the DB is hosted on localhost 5432 port

   - **For a local kind cluster:**
      ```bash
      bash scripts/manage_db_migrations.sh
      ```

   - **For a local Docker container:**
      ```bash
      bash scripts/manage_db_migrations.sh --local
      ```

   At the _`Choose an Alembic action:`_ prompt, enter `2` to upgrade.

   #### Create a New Migration
   Assuming the DB is hosted on localhost 5432 port

   - **For a local kind cluster:**
      ```bash
      bash scripts/manage_db_migrations.sh
      ```

   - **For a local Docker container:**
      ```bash
      bash scripts/manage_db_migrations.sh --local
      ```

   Steps:
   1. At the _`Choose an Alembic action:`_ prompt, enter `1` to create a new migration revision.
   2. When prompted for a migration message, enter a concise description (e.g., `add_user_table`, `update_order_status_column`).

   Migration files are created in:

   ```
   alembic/versions/
   ```

   Named as:

   ```
   <serialNumber>_<revisionId>_<migrationMessage>.py
```

### 3. Verify Migration

- Review the generated migration file(s) in `alembic/versions/`.
- Ensure the changes match your intended schema update.

To apply the migration, run:

```bash
bash scripts/manage_db_migrations.sh
```

Then enter `2` at the prompt to upgrade to the latest revision.

If errors occur, review and fix the migration script before retrying.

### 4. Merge and Apply

Once your pull request is merged, the migration changes will be applied automatically during deployment.

> **Important:** Always back up critical data before applying destructive schema changes.

## Insert Dummy Data (Optional)

You can populate your database with sample/dummy data for development, testing, or demo purposes.  
This is especially useful for local development or when you want to quickly verify API endpoints and UI features.

### 1. Prepare the Dummy Data

The dummy data SQL file is located at:

```
scripts/dummy_data.sql
```

This file contains `DELETE` statements to remove only the dummy rows (by unique IDs) and `INSERT` statements to add fresh sample data for all main tables.

### 2. Run the Insertion Script

A helper script is provided to insert the dummy data into your database, supporting both local Docker and kind cluster environments.

#### Usage

```bash
bash scripts/insert_dummy_data.sh [DB_PORT] [CONTEXT] [KUBECONFIG] [NAMESPACE] [SERVICE_NAME] [--local]
```

- `DB_PORT` (default: `5432`) — The port your PostgreSQL instance is exposed on.
- `CONTEXT` (default: `kind-sample`) — The name of your cluster context (if using Kubernetes).
- `KUBECONFIG` (default: `~/.kube/config`) — Path to your kubeconfig file (for Kubernetes access).
- `NAMESPACE` (default: `aces-orchestration-api`) — Kubernetes namespace where the database service is running.
- `SERVICE_NAME` (default: `aces-postgres`) — Name of the PostgreSQL service in your Kubernetes cluster.
- `--local` — Use this flag if your database is running locally (e.g., via Docker Compose).

#### Examples

- **For a local kind cluster (default port/cluster):**
  ```bash
  bash scripts/insert_dummy_data.sh
  ```

- **For a custom port/cluster:**
  ```bash
  bash scripts/insert_dummy_data.sh 25432 my-cluster
  ```

- **For a local Docker setup:**
  ```bash
  bash scripts/insert_dummy_data.sh --local
  ```

### 3. What the Script Does

- Removes only the dummy data rows (by unique IDs) to avoid affecting real data.
- Inserts fresh dummy data for all main tables (`alerts`, `tuning_parameters`, `workload_action`, `workload_request_decision`).
- Handles port-forwarding automatically if using a kind cluster.

### 4. When to Use

- After running migrations to verify schema and API endpoints.
- Before running integration or UI tests that require known data.
- For demos or development environments.

> **Note:**  
> The script is safe for development and test environments.  
> **Do not run this on production

