# a docker file for an sample training / mining / infer executor

FROM python:3.8.13-alpine

RUN pip3 install -r ./app/executor/requirements.txt

# tmi framework and your app
COPY app /app
RUN mkdir /img-man
COPY app/*-template.yaml /img-man/
COPY executor /app/executor

# dependencies: write other dependencies here (pytorch, mxnet, tensorboard-x, etc.)

# entry point for your app
# the whole docker image will be started with `nvidia-docker run <other options> <docker-image-name>`
# and this command will run automatically
CMD python /app/start.py
