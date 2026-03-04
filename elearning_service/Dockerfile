FROM python:3.12-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev gcc curl postgresql-client \
    libjpeg-dev zlib1g-dev && \
    pip install --upgrade pip

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Make wait-for-db.sh executable
RUN chmod +x wait-for-db.sh

CMD ["gunicorn", "elearning_service.wsgi:application", "--bind", "0.0.0.0:8003"]