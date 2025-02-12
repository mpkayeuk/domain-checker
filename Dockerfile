FROM python:3.9-slim

WORKDIR /app

COPY domain-check /app/domain-check
COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

RUN chmod +x /app/domain-check

ENTRYPOINT ["/app/domain-check"] 