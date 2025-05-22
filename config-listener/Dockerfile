FROM python:3.11-slim

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get install -y postgresql-client && apt-get clean

# Install dependencies
RUN pip install psycopg2-binary

# Unbuffered output
ENV PYTHONUNBUFFERED=1
# Make wait-for script executable
RUN chmod +x /app/wait-for-db.sh

# Use the wait-for-db script as the startup command
CMD ["/app/wait-for-db.sh"]
