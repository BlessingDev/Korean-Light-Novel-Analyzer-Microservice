FROM alpine:latest

RUN apk update
RUN apk add python3

RUN pip3 install flask flask-restful pathlib beautifulsoup4 requests

COPY . /app

WORKDIR /app

EXPOSE 80

CMD ["python3", "app.py"]