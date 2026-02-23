#!/bin/sh

# Usage: ./wait-for-db.sh db_host command args...
set -e

host="$1"
shift

echo "Waiting for Postgres at $host..."

until PGPASSWORD=$DB_PASSWORD psql -h "$host" -U "$DB_USER" -d "$DB_NAME" -c '\q' 2>/dev/null; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 2
done

>&2 echo "Postgres is up - executing command"
exec "$@"
