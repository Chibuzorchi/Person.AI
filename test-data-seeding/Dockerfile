FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY data_generators/ ./data_generators/
COPY scripts/ ./scripts/

CMD ["python", "scripts/seed_data.py"]
