#!/bin/sh
set -eu
# psql literal binding keeps passwords out of SQL interpolation and stdout.
psql --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" --set ON_ERROR_STOP=1 --set app_password="$APP_DATABASE_PASSWORD" <<'SQL'
SELECT format('CREATE ROLE app LOGIN PASSWORD %L', :'app_password') \gexec
ALTER DATABASE app OWNER TO app;
GRANT USAGE, CREATE ON SCHEMA public TO app;
SQL
