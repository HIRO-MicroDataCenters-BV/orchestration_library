#!/bin/bash

set -e

# Usage: ./scripts/insert_dummy_data.sh [PORT] [CONTEXT] [KUBECONFIG] [NAMESPACE] [SERVICE_NAME] [--local]
DATABASE_PORT=5432
CLUSTER_NAME="sample"
CONTEXT="kind-sample"
KUBECONFIG="$HOME/.kube/config"
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
      elif [[ -z "$CONTEXT_SET" ]]; then
        CONTEXT="$arg"
        CONTEXT_SET=1
      elif [[ -z "$KUBECONFIG_SET" ]]; then
        KUBECONFIG="$arg"
        KUBECONFIG_SET=1
      elif [[ -z "$NAMESPACE_SET" ]]; then
        NAMESPACE="$arg"
        NAMESPACE_SET=1
      elif [[ -z "$SERVICE_NAME_SET" ]]; then
        SERVICE_NAME="$arg"
        SERVICE_NAME_SET=1
      else
        echo "Unknown argument: $arg"
        exit 1
      fi
      shift
      ;;
  esac
done

if [ "$LOCAL_MODE" -eq 0 ]; then
  echo "Remove the port-forwarding on the database service"
  if pgrep -f "kubectl port-forward service/$SERVICE_NAME -n $NAMESPACE $DATABASE_PORT:5432 --context $CONTEXT" --kubeconfig $KUBECONFIG > /dev/null; then
    pkill -f "kubectl port-forward service/$SERVICE_NAME -n $NAMESPACE $DATABASE_PORT:5432 --context $CONTEXT" --kubeconfig $KUBECONFIG
  fi

  echo "Port-forwarding the database service to localhost:$DATABASE_PORT"
  kubectl port-forward service/$SERVICE_NAME -n $NAMESPACE $DATABASE_PORT:5432 --context $CONTEXT --kubeconfig $KUBECONFIG &

  echo "Wait for port-forwarding to be ready"
  sleep 5
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
  pkill -f "kubectl port-forward service/$SERVICE_NAME -n $NAMESPACE $DATABASE_PORT:5432 --context $CONTEXT" --kubeconfig $KUBECONFIG
fi

echo "Dummy data inserted successfully."