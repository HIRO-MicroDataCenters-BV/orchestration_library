#!/bin/bash

# Exit on any error
set -e

LUSTER_NAME=${1:-sample}

if [ -z "$CLUSTER_NAME" ]; then
  echo "Usage: $0 <cluster-name>"
  exit 1
fi

# Check if alembic is installed
if ! command -v alembic &> /dev/null; then
  echo "Alembic not found. Please install it with 'pip install alembic'."
  exit 1
fi

# Read database local Port from arguments which is port-forwarded to the database service
# If not provided, default to 35432
if [ -z "$2" ]; then
  export DATABASE_PORT=35432
else
  export DATABASE_PORT="$2"
fi


echo "Port-forwarding the database service to localhost:$DATABASE_PORT"
kubectl port-forward service/postgres -n orchestration-api $DATABASE_PORT:5432 --context kind-$CLUSTER_NAME &

echo "Wait for port-forwarding to be ready"
sleep 5


# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    # Export the database URL
    export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:$DATABASE_PORT/orchestration_db"
fi

echo "Using database: $DATABASE_URL"

# Ask for action
echo "Choose an Alembic action:"
echo "1) Create new revision"
echo "2) Upgrade to latest"
echo "3) Downgrade last migration"
echo "4) Show current revision"
echo "5) History"
echo "6) Stamp head"
read -rp "Enter your choice [1-6]: " choice

case $choice in
  1)
    read -rp "Enter migration message: " message
    alembic revision --autogenerate -m "$message"
    ;;
  2)
    alembic upgrade head
    ;;
  3)
    alembic downgrade -1
    ;;
  4)
    alembic current
    ;;
  5)
    alembic history --verbose
    ;;
  6)
    alembic stamp head
    ;;
  *)
    echo "Invalid choice."
    exit 1
    ;;
esac

echo "Remove the port-forwarding on the database service"
pkill -f "kubectl port-forward service/postgres -n orchestration-api $DATABASE_PORT:5432 --context kind-$CLUSTER_NAME"

echo "Done."
