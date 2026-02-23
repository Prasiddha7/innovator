#!/bin/sh
# wait-for-db.sh

host="$1"
shift
cmd="$@"

until PGPASSWORD=$DB_PASSWORD psql -h "$host" -U "$DB_USER" -d "$DB_NAME" -c '\q'; do
  echo "Waiting for database at $host..."
  sleep 2
done

exec $cmd
