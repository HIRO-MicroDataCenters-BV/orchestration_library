#!/bin/bash

set -e

DATABASE_PORT=5432
CLUSTER_NAME="sample"
NAMESPACE="aces-orchestration-api"
SERVICE_NAME="aces-postgres"
LOCAL_MODE=0
SQL_FILE="scripts/dummy_data.sql"

# Parse arguments
for arg in "$@"; do
  case $arg in
    --local|-l)
      LOCAL_MODE=1
      shift
      ;;
    *)
      if [[ -z "$DATABASE_PORT_SET" ]]; then
        DATABASE_PORT="$arg"
        DATABASE_PORT_SET=1
      elif [[ -z "$CLUSTER_NAME_SET" ]]; then
        CLUSTER_NAME="$arg"
        CLUSTER_NAME_SET=1
      fi
      shift
      ;;
  esac
done

if [ "$LOCAL_MODE" -eq 0 ]; then
  echo "Remove the port-forwarding on the database service"
  if pgrep -f "kubectl port-forward service/$SERVICE_NAME -n $NAMESPACE $DATABASE_PORT:5432 --context kind-$CLUSTER_NAME" > /dev/null; then
    pkill -f "kubectl port-forward service/$SERVICE_NAME -n $NAMESPACE $DATABASE_PORT:5432 --context kind-$CLUSTER_NAME"
  fi

  echo "Port-forwarding the database service to localhost:$DATABASE_PORT"
  kubectl port-forward service/$SERVICE_NAME -n $NAMESPACE $DATABASE_PORT:5432 --context kind-$CLUSTER_NAME &

  echo "Wait for port-forwarding to be ready"
  sleep 3
fi

# Check if psql is installed
if ! command -v psql &> /dev/null; then
  echo "psql not found. Please install it (e.g., 'brew install libpq')."
  exit 1
fi

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    export DATABASE_URL="postgresql://postgres:postgres@localhost:$DATABASE_PORT/orchestration_db"
fi

# Extract connection parameters from DATABASE_URL
PGUSER=$(echo "$DATABASE_URL" | sed -n 's|.*//\([^:]*\):.*|\1|p')
PGPASSWORD=$(echo "$DATABASE_URL" | sed -n 's|.*//[^:]*:\([^@]*\)@.*|\1|p')
PGHOST=$(echo "$DATABASE_URL" | sed -n 's|.*@\(.*\):[0-9]*/.*|\1|p')
PGPORT=$(echo "$DATABASE_URL" | sed -n 's|.*:\([0-9]*\)/.*|\1|p')
PGDATABASE=$(echo "$DATABASE_URL" | sed -n 's|.*/\(.*\)$|\1|p')

export PGPASSWORD

echo "Inserting dummy data into $PGDATABASE at $PGHOST:$PGPORT as $PGUSER"
psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" -f "$SQL_FILE"

if [ "$LOCAL_MODE" -eq 0 ]; then
  echo "Remove the port-forwarding on the database service"
  pkill -f "kubectl port-forward service/$SERVICE_NAME -n $NAMESPACE $DATABASE_PORT:5432 --context kind-$CLUSTER_NAME"
fi

echo "Dummy data inserted successfully."