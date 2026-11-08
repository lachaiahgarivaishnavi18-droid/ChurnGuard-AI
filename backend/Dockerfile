FROM python:3.12-slim
WORKDIR /project
COPY backend/requirements.txt backend/requirements.txt
COPY backend/requirements-lock.txt backend/requirements-lock.txt
RUN pip install --no-cache-dir -r backend/requirements.txt -c backend/requirements-lock.txt
COPY backend backend
COPY trained_models trained_models
COPY dataset dataset
WORKDIR /project/backend
CMD ["sh", "-c", "flask --app run db upgrade && gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 run:app"]
