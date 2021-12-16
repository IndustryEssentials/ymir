ARG IMAGE=python:3.8.10
FROM ${IMAGE}

RUN git config --global user.name 'Deployer'
RUN git config --global user.email 'deployer@ymir.ai'

COPY requirements.txt /dist/

RUN pip install -r /dist/requirements.txt

WORKDIR /workplace

COPY . /workplace/

RUN python setup.py install && rm -rf *

COPY tutorial ./tutorial

CMD echo "workplace ready\n" && mir -v
