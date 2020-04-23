# pull official base image
FROM python:3.8.2-alpine

# set work directory
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
COPY ./requirements.txt /app_files/requirements.txt
# copy entrypoint.sh
COPY ./entrypoint.sh /app_files/entrypoint.sh

RUN \
  pip install --upgrade pip && \
  pip install -r /app_files/requirements.txt && \
  adduser --disabled-password --gecos '' user

USER user

