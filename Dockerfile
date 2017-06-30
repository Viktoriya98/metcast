FROM alpine

RUN apk update
RUN apk upgrade
RUN apk add python3

COPY . /app
WORKDIR /app

RUN pip3 install -r requirements.txt

EXPOSE 5000

ENTRYPOINT ["python3"]

CMD ["app.py"]
