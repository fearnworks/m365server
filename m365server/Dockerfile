FROM python:3.11
ENV PYTHONFAULTHANDLER=1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV MPLCONFIGDIR /tmp/matplotlib

RUN --mount=type=cache,target=/var/cache/apt,id=apt \
    apt-get update && apt-get -y upgrade
RUN apt-get update && apt-get -y install procps net-tools tini

RUN python3 -m pip install --upgrade pip

# Create appuser
RUN groupadd -r appuser && useradd --no-log-init -r -g appuser appuser

# Create app directory and change ownership to appuser
RUN mkdir /app && \
    mkdir -p /home/appuser/.cache && \
    chown -R appuser:appuser /app /home/appuser

COPY ./requirements/requirements.txt /app/requirements.txt
# Set environment variables
RUN --mount=type=cache,target=~/.cache/pip \
    pip install -r /app/requirements.txt

# Set working directory to /app
WORKDIR /app

COPY --chown=appuser:appuser  . /app/m365server
USER appuser
WORKDIR /app/m365server
RUN python3 -m pip install -e .

ENTRYPOINT ["tini", "--","uvicorn", "m365server.main:app", "--host", "0.0.0.0", "--port", "17200", "--reload"]
