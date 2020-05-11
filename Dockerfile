FROM python:3

COPY . /scholarly_app

RUN pip install -r /scholarly_app/requirements.txt

ADD *.sh /

ENTRYPOINT ["/entrypoint.sh"]
