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

## Database Schema Changes

To make changes to the database schema, follow these steps:

1. **Add or update models**

   Make your schema changes by modifying or adding files in:

   ```
   app/models/
   ```

2. **Generate Alembic migration**

   To generate a new Alembic migration file:

   1. Run the migration script:
      ```
      bash scripts/db_migrate.sh
      ```
   2. When prompted with "_Choose an Alembic action:_", enter `1` to create a new revision.
   3. Next, when asked "_Enter migration message:_", provide a brief description of your schema changes (for example, "add user table" or "update order status column").  
   
   A new migration file will be created in the versions directory, named in the format `revisionId_migrationMessage.py`.

3. **Verify migration**

   Review the newly generated migration file(s) in `alembic/versions/` and ensure the changes accurately reflect your intended schema updates.

   Next, run the migration script again and select option `2` at the "_Choose an Alembic action:_" prompt to upgrade the database to the latest revision.  
   
   If the migration completes successfully, you can proceed to push your changes.  
   If there are any errors, review and fix the issues in the generated migration file(s) before retrying.

4. **Merge and apply**

   Once your pull request is merged, the migration changes will be applied automatically during deployment.

   **Note:** Always back up important data before making destructive changes to the database.

---
