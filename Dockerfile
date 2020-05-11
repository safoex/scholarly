FROM python:3

COPY . /scholarly_app

RUN pip install -r /scholarly_app/requirements.txt

ADD *.sh /
RUN chmod +X /entrypoint.sh
RUN chmod +X /scholarly_app/scholarly/manual_test.py

ENTRYPOINT ["/entrypoint.sh"]
