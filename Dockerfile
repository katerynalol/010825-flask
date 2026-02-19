FROM nginx:alpine3.23-perl

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && pip install -r requirements.txt