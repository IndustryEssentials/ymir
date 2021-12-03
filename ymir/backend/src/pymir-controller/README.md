# pyimr-controller

> https://github.com/scalable-ai/pymir-controller

## Features

- Receive the request from pymir-backend,do some logic then call pymir-command 

## Development
To install dev dependencies you can use the following command:
```shell script
pip3 install -r requirements.txt&&pip3 install -r requirements-dev.txt 
```

To run server locally:
- set your server_prd_config.yaml, some path for persistence files
- start pymir-controller server you can use the following command
```
supervisord -nc supervisor/supervisord.conf
```
Then you can see the folder called `./logs`, which including logs there


### Running Tests
Unit tests are within the tests folder and we recommend to run them using `tox`.
```
tox
```