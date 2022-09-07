# pull the official docker image
FROM python:3.9.5

# RUN apk add --no-cache --virtual .build-deps gcc musl-dev \
#  && pip install cython \
#  && apk del .build-deps gcc musl-dev
# set work directory
WORKDIR /cryptomonitor

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# copy project
