#!/bin/bash

# -----------------------------
# Innovator Microservices Setup
# -----------------------------

services=("auth" "kms" "elearning" "ecommerce" "socialmedia")
db_port=5433
service_port=8000

echo "Generating .env files, Docker Compose, JWT keys..."

# Create .env files
for svc in "${services[@]}"; do
  mkdir -p ./${svc}_service
  cat > ./${svc}_service/.env <<EOL
DEBUG=True
SECRET_KEY=super-secret-${svc}-key
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=${svc}_db
DB_USER=innovator_user
DB_PASSWORD=StrongPassword123
DB_HOST=${svc}_db
DB_PORT=5432

JWT_ALGORITHM=RS256
JWT_PUBLIC_KEY_PATH=../auth_service/public.pem
JWT_PRIVATE_KEY_PATH=./private.pem
EOL
done

# Create docker-compose.yml
cat > docker-compose.yml <<EOL
version: '3.9'
services:
EOL

for svc in "${services[@]}"; do
  cat >> docker-compose.yml <<EOL

  ${svc}_db:
    image: postgres:15
    environment:
      POSTGRES_DB: ${svc}_db
      POSTGRES_USER: innovator_user
      POSTGRES_PASSWORD: StrongPassword123
    ports:
      - "${db_port}:5432"

  ${svc}_service:
    build: ./${svc}_service
    env_file: ./${svc}_service/.env
    volumes:
      - ./${svc}_service:/app
    ports:
      - "${service_port}:${service_port}"
    depends_on:
      - ${svc}_db
EOL
  db_port=$((db_port+1))
  service_port=$((service_port+1))
done

# Generate JWT keys for auth_service
mkdir -p auth_service
cd auth_service
if [ ! -f private.pem ]; then
  openssl genrsa -out private.pem 2048
  openssl rsa -in private.pem -pubout -out public.pem
  echo "JWT keys generated for auth_service."
else
  echo "JWT keys already exist."
fi
cd ..

echo "Setup complete! Run: docker-compose build && docker-compose up"
