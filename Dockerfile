FROM alpine

RUN apk update
RUN apk upgrade
RUN apk add python3

ADD . /app
WORKDIR /app

RUN pip3 install -r requirements.txt
