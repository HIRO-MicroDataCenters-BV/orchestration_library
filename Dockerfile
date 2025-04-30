FROM python:3.13-slim

WORKDIR /code

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY orchestrationAPI/ ./orchestrationAPI

CMD ["uvicorn", "orchestrationAPI.main:app", "--host", "0.0.0.0", "--port", "8000"]
