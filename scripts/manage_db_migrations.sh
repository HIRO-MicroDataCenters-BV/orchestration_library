#!/bin/bash

# Exit on any error
set -e

# Usage: ./scripts/manage_db_migrations.sh [PORT] [CONTEXT] [KUBECONFIG] [NAMESPACE] [SERVICE_NAME] [--local]
DATABASE_PORT=5432
CLUSTER_NAME="sample"
CONTEXT="kind-sample"
KUBECONFIG="$HOME/.kube/config"
NAMESPACE="aces-orchestration-api"
SERVICE_NAME="aces-postgres"
LOCAL_MODE=0

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
  sleep 3
fi

# Check if alembic is installed
if ! command -v alembic &> /dev/null; then
  echo "Alembic not found. Please install it with 'pip install alembic'."
  exit 1
fi

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    # Export the database URL
    export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:$DATABASE_PORT/orchestration_db"
fi

echo "Using database: $DATABASE_URL"

rename_latest_revision_file() {
  local message="$1"
  local latest_file="$2"
  local versions_dir="$3"

  # Find the newest migration file created
  newfile=$(ls -t "$versions_dir"/*.py | head -n 1)

  if [ "$newfile" == "$latest_file" ]; then
    echo "No schema changes detected. No new migration created. Skipping rename."
    return 0
  fi

  # Extract the revision ID from filename
  filename=$(basename "$newfile")
  revision_id=$(echo "$filename" | cut -d'_' -f1)

  # Count existing migration files before rename (excluding this one)
  serial=$(ls "$versions_dir"/*.py | grep -v "$filename" | wc -l | xargs)
  serial=$((serial + 1))  # increment for new file
  serial=$(printf "%03d" "$serial")  # zero-padded

  # Sanitize the migration message
  safe_message=$(echo "$message" | tr '[:space:]' '_' | tr -cd '[:alnum:]_')

  # New filename
  newname="${serial}_${revision_id}_${safe_message}.py"

  mv "${newfile}" "${versions_dir}/${newname}"
  echo "Renamed migration to: ${newname}"
}

# Ask for action
echo "Choose an Alembic action:"
echo "1) Create new revision"
echo "2) Upgrade to latest"
echo "3) Upgrade one migration"
echo "4) Downgrade last migration"
echo "5) Show current revision"
echo "6) History"
echo "7) Stamp head"
read -rp "Enter your choice [1-7]: " choice

case $choice in
  1)
    versions_dir="alembic/versions"
    # Get the latest file before creating a new revision
    latest_file=$(ls -t "$versions_dir"/*.py | head -n 1)
    read -rp "Enter migration message: " message
    alembic revision --autogenerate -m "$message"
    rename_latest_revision_file "$message" "$latest_file" "$versions_dir"
    ;;
  2)
    alembic upgrade head
    ;;
  3)
    alembic upgrade +1
    ;;
  4)
    alembic downgrade -1
    ;;
  5)
    alembic current
    ;;
  6)
    alembic history --verbose
    ;;
  7)
    alembic stamp head
    ;;
  *)
    echo "Invalid choice."
    exit 1
    ;;
esac

if [ "$LOCAL_MODE" -eq 0 ]; then
  echo "Remove the port-forwarding on the database service"
  pkill -f "kubectl port-forward service/$SERVICE_NAME -n $NAMESPACE $DATABASE_PORT:5432 --context $CONTEXT" --kubeconfig $KUBECONFIG
fi

echo "Done."
