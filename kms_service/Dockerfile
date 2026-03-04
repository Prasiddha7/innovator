# Use slim Python image
FROM python:3.13-slim

# Prevent python from writing pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev gcc curl postgresql-client \
    libjpeg-dev zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*


# Copy requirements first (better caching)
COPY requirements.txt .

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Expose Django port
EXPOSE 8002

# Default command (can be overridden)
CMD ["gunicorn", "kms_service.wsgi:application", "--bind", "0.0.0.0:8002"]