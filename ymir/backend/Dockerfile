FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
  && apt-get install -y git \
  && apt-get install -y --no-install-recommends python3-pip python3-dev \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip

RUN pip install --no-cache-dir "uvicorn[standard]" gunicorn

RUN mkdir -p /data/sharing/
RUN mkdir -p /app_logs/

COPY requirements.txt ./
RUN pip3 install -r requirements.txt

COPY ./src /app
WORKDIR /app

COPY ./deploy/git.config /root/.gitconfig


COPY ./deploy/supervisor /app/supervisor

ENV PYTHONPATH=/app/pymir-app:/app/pymir-controller:/app/pymir-viz:/app/common
