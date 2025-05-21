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
   kubectl port-forward svc/orchestration-api 8000:8000 -n orchestration-api
   ```

   Now you can access the application locally at:  
   [http://localhost:8010](http://localhost:8010)

---
