FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY test_runner/ ./test_runner/
COPY tests/ ./tests/
COPY scripts/ ./scripts/

# Create output directory
RUN mkdir -p /app/output

CMD ["python", "test_runner/e2e_test_runner.py"]
