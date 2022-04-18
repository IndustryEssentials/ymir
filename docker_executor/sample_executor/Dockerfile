# a docker file for an sample training / mining / infer executor

FROM nvidia/cuda:10.1-cudnn7-devel-ubuntu18.04

# dependencies: python 3.8 and pip
RUN apt-get update
RUN apt install -y software-properties-common wget
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get update
RUN apt install -y python3.8 python3-distutils
RUN ln -s /usr/bin/python3.8 /usr/bin/python
RUN wget https://bootstrap.pypa.io/get-pip.py && python get-pip.py

# tmi framework and your app
COPY app /app
RUN mkdir /img-man
COPY app/*-template.yaml /img-man/
COPY executor /app/executor
RUN pip3 install -r /app/executor/requirements.txt

# dependencies: write other dependencies here (pytorch, mxnet, tensorboard-x, etc.)

# entry point for your app
# the whole docker image will be started with `nvidia-docker run <other options> <docker-image-name>`
# and this command will run automatically
CMD python /app/start.py
