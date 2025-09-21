FROM python:3.9-slim

WORKDIR /app

# Install dependencies in one optimized layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl gcc python3-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install Python packages with better caching
COPY requirements.txt .
RUN pip install --no-cache-dir --disable-pip-version-check -r requirements.txt

# Copy application code
COPY . .

EXPOSE 8001

# Add health check
HEALTHCHECK --interval=10s --timeout=3s --start-period=3s --retries=2 \
  CMD curl -f http://localhost:8001/health || exit 1

CMD ["python", "app.py"]
