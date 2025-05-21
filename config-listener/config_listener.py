import os
import psycopg2
import time

# Load environment variables
DB_NAME = os.getenv("DB_NAME", "orchestration_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", 5432)

# Retry loop until DB is ready
while True:
    try:
        print("Attempting DB connection...")
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
        )
        print("Connected to DB. Listening for config changes...")
        break
    except psycopg2.OperationalError as e:
        print(f" Waiting for DB... {e}")
        time.sleep(2)

# Start listening
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
cur = conn.cursor()
cur.execute("LISTEN new_config;")

print(" Listening on channel 'new_config'...")
while True:
    conn.poll()
    print("Polling for notifications...", flush=True)
    while conn.notifies:
        notify = conn.notifies.pop(0)
        print(f"New config notification received: {notify.payload}", flush=True)
    time.sleep(5)
