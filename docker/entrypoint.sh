#!/usr/bin/env sh
set -e

# Wait for DB if DATABASE_URL is postgres
if echo "$DATABASE_URL" | grep -qiE '^postgresql://|^postgres://'; then
	echo "Waiting for Postgres to be ready..."
	# Basic wait loop using pg_isready if available, else sleep
	ATTEMPTS=0
	MAX_ATTEMPTS=60
	until python - <<'PY'
import os, sys
from urllib.parse import urlparse
import socket
url = os.environ.get('DATABASE_URL', '')
if url.startswith('postgres://'):
		url = url.replace('postgres://', 'postgresql://', 1)
u = urlparse(url)
host, port = u.hostname, u.port or 5432
s = socket.socket()
s.settimeout(1)
try:
		s.connect((host, port))
		print('ok')
except Exception:
		sys.exit(1)
PY
	do
		ATTEMPTS=$((ATTEMPTS+1))
		if [ "$ATTEMPTS" -ge "$MAX_ATTEMPTS" ]; then
			echo "Database not reachable after ${MAX_ATTEMPTS}s" >&2
			exit 1
		fi
		sleep 1
	done
fi

echo "Running Alembic migrations..."
alembic upgrade head || true

echo "Starting Uvicorn..."
exec python -m uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}

