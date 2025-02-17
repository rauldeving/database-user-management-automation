FROM python:3.11-slim

WORKDIR /app

COPY manage_users.py requirements.txt users.yaml ./

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python", "manage_users.py"]
