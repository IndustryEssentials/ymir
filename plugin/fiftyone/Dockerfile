FROM python:3.9

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --upgrade pip


RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt 

COPY . /code

EXPOSE 8080

CMD ["uvicorn" , "--host=0.0.0.0", "--port=8080", "app.main:app" ]
