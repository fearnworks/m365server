FROM python:3.11-slim

ENV PYTHONFAULTHANDLER=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MPLCONFIGDIR=/tmp/matplotlib \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    HOME=/app

RUN apt-get update && apt-get -y upgrade \
    && apt-get -y install --no-install-recommends \
        procps \
        net-tools \
        tini \
    && rm -rf /var/lib/apt/lists/*

# Create appuser and app directory
RUN groupadd -r appuser && useradd --no-log-init -r -g appuser appuser \
    && mkdir /app \
    && chown -R appuser:appuser /app

WORKDIR /app

# Install Python dependencies
COPY ./m365server/requirements/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=appuser:appuser ./m365server ./m365server

# Switch to non-root user
USER appuser

# Install application
WORKDIR /app/m365server
RUN pip install --no-cache-dir -e .

ENTRYPOINT ["tini", "--", "bash", "run.sh"]