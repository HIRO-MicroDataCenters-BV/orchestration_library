#!/bin/sh

# Wait for PostgreSQL to be available
echo "Waiting for PostgreSQL at $DB_HOST:$DB_PORT..."

until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER"; do
  sleep 1
done

echo "PostgreSQL is ready. Starting listener..."

# Start your Python config listener
exec python -u /app/config_listener.py
