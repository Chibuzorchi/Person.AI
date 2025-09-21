FROM python:3.9-slim

WORKDIR /app

# Install curl and build tools for psutil
RUN apt-get update && apt-get install -y curl gcc python3-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8001

CMD ["python", "app.py"]
