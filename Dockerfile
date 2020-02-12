FROM python:3.8-alpine
MAINTAINER "Prasanjit Prakash"

# do then when running in docker container
# doesn't allow python to buffer output in
# which avoids complications within containers
ENV PYTHONUNBUFFERED 1 
COPY ./requirements.txt /requirements.txt
COPY pytest.ini /pytest.ini


RUN apk add --update --no-cache postgresql-client
RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libc-dev linux-headers postgresql-dev musl-dev
RUN pip install -r /requirements.txt
RUN apk del .tmp-build-deps


RUN mkdir /app
RUN mkdir /.pytest_cache
WORKDIR /app
COPY ./api /app

# this is for security purpose
# if someone compromises the application
# they have complete access to our container
RUN adduser -D www
RUN chown -R www /.pytest_cache
USER www
