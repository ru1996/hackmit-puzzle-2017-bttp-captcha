FROM python:2

ARG APP_PATH=/captcha

#RUN apk --update add python py-pip python-dev build-base linux-headers
#RUN apk --update add  openssl python3 python-dev build-base linux-headers
#RUN update-ca-certificates

ENV PYTHONUNBUFFERED 1

#RUN apk --update add python py-pip python-dev build-base linux-headers py-gevent
# py-gevent
COPY requirements.txt $APP_PATH/requirements.txt
RUN pip install -r $APP_PATH/requirements.txt
RUN pip install uwsgi

COPY . $APP_PATH

WORKDIR $APP_PATH

CMD ["uwsgi", "--chdir", "app", "--http", ":8000", "--wsgi-file", "app.py", "--callable", "app"]

