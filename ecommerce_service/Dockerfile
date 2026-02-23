FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev gcc curl && \
    pip install --upgrade pip

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Make wait-for-db.sh executable
RUN chmod +x wait-for-db.sh

CMD ["./wait-for-db.sh", "ecommerce_db", "python", "manage.py", "runserver", "0.0.0.0:8000"]
