# Orchestration Library

## Overview

This project contains a FastAPI-based backend and a PostgreSQL database container that initializes with tables on startup using SQL scripts.

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
   bash scripts/kind_cluster_init.sh             # Uses default cluster name 'kind-sample'
   bash scripts/kind_cluster_init.sh my-cluster  # Uses 'my-cluster' as the cluster name
   ```

2. **Build and deploy the application**

   Use the following script to build and deploy the application inside the kind cluster.  
   If you specified a custom cluster name above, pass the same parameter here.

   ```bash
   bash scripts/deploy_app.sh                    # Deploys to 'kind-sample' by default
   bash scripts/deploy_app.sh my-cluster         # Deploys to 'my-cluster'
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
      ```
      bash scripts/db_migrate.sh [DB_PORT] [CLUSTER_NAME] [--local]
      ```

      - `DB_PORT` (default: `5432`)
      - `CLUSTER_NAME` (default: `sample`)
      - `--local` (use for Docker setup)

   #### Upgrade Before Creating Migration
   
   Ensure your local database is up to date:

   ```bash
   bash scripts/db_migrate.sh
   ```

   At the _`Choose an Alembic action:`_ prompt, enter `2` to upgrade.

   #### Create a New Migration
   Assuming the DB is hosted on localhost 5432 port

   - **For a local kind cluster:**
      ```bash
      bash scripts/db_migrate.sh
      ```

   - **For a local Docker container:**
      ```bash
      bash scripts/db_migrate.sh --local
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
bash scripts/db_migrate.sh
```

Then enter `2` at the prompt to upgrade to the latest revision.

If errors occur, review and fix the migration script before retrying.

### 4. Merge and Apply

Once your pull request is merged, the migration changes will be applied automatically during deployment.

> **Important:** Always back up critical data before applying destructive schema changes.
