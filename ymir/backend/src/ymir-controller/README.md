# YMIR-CONTROLLER

> https://github.com/IndustryEssentials/ymir

## Features

- Receive the request from ymir-backend,do some logic then call ymir-command

## Development
To install dev dependencies you can use the following command:
```shell script
pip3 install -r requirements.txt&&pip3 install -r requirements-dev.txt
```

To run server locally:
- set your server_prd_config.yaml, some path for persistence files
- start ymir-controller server you can use the following command
```
supervisord -nc supervisor/supervisord.conf
```
Then you can see the folder called `./logs`, which including logs there


### Running Tests
Unit tests are within the tests folder and we recommend to run them using `tox`.
```
tox
```