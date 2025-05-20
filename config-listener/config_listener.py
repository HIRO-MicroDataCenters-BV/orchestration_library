import psycopg2
import select
import json
import os

print("🔄 Starting config change listener...")

conn = psycopg2.connect(
    dbname=os.environ.get("DB_NAME", "orchestration_db"),
    user=os.environ.get("DB_USER", "postgres"),
    password=os.environ.get("DB_PASSWORD", "postgres"),
    host=os.environ.get("DB_HOST", "db"),
    port=os.environ.get("DB_PORT", "5432")
)

conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
cur = conn.cursor()
cur.execute("LISTEN new_config;")
print("Listening on channel 'new_config'...")

while True:
    if select.select([conn], [], [], 10) == ([], [], []):
        continue  # Timeout waiting for notification
    conn.poll()
    while conn.notifies:
        notify = conn.notifies.pop(0)
        print("Received new config notification:")
        print(json.dumps(json.loads(notify.payload), indent=2))
