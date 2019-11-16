FROM python:3.7

LABEL maintainer="emanuele.palazzetti@gmail.com"

COPY . /app
RUN pip install -r /app/requirements.txt
WORKDIR /app