#!/bin/bash

# Exit on any error
set -e

CLUSTER_NAME=${1:-sample}

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

echo "Remove the port-forwarding on the database service"
if pgrep -f "kubectl port-forward service/postgres -n orchestration-api $DATABASE_PORT:5432 --context kind-$CLUSTER_NAME" > /dev/null; then
  pkill -f "kubectl port-forward service/postgres -n orchestration-api $DATABASE_PORT:5432 --context kind-$CLUSTER_NAME"
fi

echo "Port-forwarding the database service to localhost:$DATABASE_PORT"
kubectl port-forward service/postgres -n orchestration-api $DATABASE_PORT:5432 --context kind-$CLUSTER_NAME &

echo "Wait for port-forwarding to be ready"
sleep 3


# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    # Export the database URL
    export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:$DATABASE_PORT/orchestration_db"
fi

echo "Using database: $DATABASE_URL"

rename_latest_revision_file() {
  local message="$1"
  local versions_dir="alembic/versions"

  # Find the newest migration file created
  newfile=$(ls -t "$versions_dir"/*.py | head -n 1)

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
echo "3) Downgrade last migration"
echo "4) Show current revision"
echo "5) History"
echo "6) Stamp head"
read -rp "Enter your choice [1-6]: " choice

case $choice in
  1)
    read -rp "Enter migration message: " message
    alembic revision --autogenerate -m "$message"
    rename_latest_revision_file "$message"
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
