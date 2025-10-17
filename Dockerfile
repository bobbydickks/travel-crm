## Base image
FROM python:3.12-slim

# Prevent Python from writing .pyc files and enable unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps (git optional, tzdata for correct time, build tools if needed)
RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
	   tzdata \
	&& rm -rf /var/lib/apt/lists/*

# Install Python deps first (leverage Docker layer cache)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY alembic.ini ./
COPY alembic ./alembic
COPY src ./src
COPY static ./static
COPY templates ./templates
COPY docker/entrypoint.sh /entrypoint.sh

# Make entrypoint executable
RUN chmod +x /entrypoint.sh

EXPOSE 8000

# Default envs (can be overridden at runtime)
ENV PORT=8000

CMD ["/entrypoint.sh"]

