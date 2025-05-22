""" Monitor data change in postgres configuration table"""
import os
import psycopg2
import select
import json
print("Config listener started")

#  Load database config from environment variables
DB_NAME = "orchestration_db"#os.getenv("DB_NAME", "orchestration_db")
DB_USER = "postgres"# os.getenv("DB_USER", "postgres")
DB_PASSWORD = "postgres"#os.getenv("DB_PASSWORD", "postgres")
DB_HOST = "db" #os.getenv("DB_HOST", "db")
DB_PORT = 5432 #os.getenv("DB_PORT", 5432)

# print("DEBUG: ENVIRONMENT VARS")
# print(f"DB_NAME: {DB_NAME}")
# print(f"DB_USER: {DB_USER}")
# print(f"DB_PASSWORD: {DB_PASSWORD}")
# print(f"DB_HOST: {DB_HOST}")
# print(f"DB_PORT: {DB_PORT}")

print(" Starting PostgreSQL config change listener...")

try:
    #  Establish database connection
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

    #  Enable autocommit so LISTEN/NOTIFY works properly
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

    #  Open a cursor and listen on the 'new_config' channel
    cur = conn.cursor()
    cur.execute("LISTEN new_config;")
    print("Listening for notifications on channel 'new_config'...")

    #  Wait for incoming notifications efficiently
    while True:
        print("in first while loop")
        # `select` blocks until conn is ready for reading (a new NOTIFY)
        if select.select([conn], [], [], None):
            conn.poll() # Pull the new messages
            while conn.notifies:
                print("in 2nd while loop")
                notify = conn.notifies.pop(0)
                try:
                    data = json.loads(notify.payload)
                    print(f"Received notification: {data}")
                    # You can add logic here to handle the config update
                except json.JSONDecodeError:
                    print(f" Malformed JSON payload: {notify.payload}")

except KeyboardInterrupt:
    print("Listener stopped by user.")

except Exception as e:
    print(f"Error: {e}")
#
# finally:
#     # Clean up if needed
#     if 'cur' in locals(): cur.close()
#     if 'conn' in locals(): conn.close()
