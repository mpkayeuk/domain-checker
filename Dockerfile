FROM python:3.9-slim

WORKDIR /app

COPY domain_check.py /app/domain_check.py
COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

RUN chmod +x /app/domain_check.py

ENTRYPOINT ["/app/domain_check.py"]
