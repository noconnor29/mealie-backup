FROM python:3.14-rc-alpine3.20

WORKDIR /app

# Testing: Install required tools: ping and curl
RUN apt-get update && \
    apt-get install -y --no-install-recommends iputils-ping curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY ./app/requirements.txt .
COPY ./app/mealie-backup.py .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "/app/mealie-backup.py"]