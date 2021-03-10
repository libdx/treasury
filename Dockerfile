FROM python:3.9.0-slim-buster

RUN apt-get update && \
    apt-get -y install netcat gcc postgresql && \
    apt-get clean

RUN pip install --upgrade pip
COPY ./requirements.txt .
COPY ./requirements-dev.txt .
RUN pip install -r requirements.txt
RUN pip install -r requirements-dev.txt

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . .

COPY ./entrypoint.sh .
RUN chmod +x /usr/src/app/entrypoint.sh
