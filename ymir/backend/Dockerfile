FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

ARG PIP_SOURCE=https://pypi.org/simple

ARG SERVER_MODE=prod

RUN apt-get update \
  && apt-get install -y git \
  && apt-get install -y --no-install-recommends python3-pip python3-dev \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip

RUN pip install --no-cache-dir "uvicorn[standard]" gunicorn -i ${PIP_SOURCE}

RUN mkdir -p /data/sharing/
RUN mkdir -p /app_logs/

COPY requirements.txt ./
RUN pip3 install -r requirements.txt -i ${PIP_SOURCE}

RUN if [ "$SERVER_MODE" = "dev" ]; then \
    pip3 uninstall -y ymir-cmd && \
    pip3 install --force-reinstall -U "git+https://github.com/IndustryEssentials/ymir.git/@dev#egg=ymir-cmd&subdirectory=ymir/command"; \
  fi

COPY ./src /app
WORKDIR /app

COPY ./deploy/git.config /root/.gitconfig


COPY ./deploy/supervisor /app/supervisor

ENV PYTHONPATH=/app/ymir-app:/app/ymir-controller:/app/ymir-viz:/app/common
