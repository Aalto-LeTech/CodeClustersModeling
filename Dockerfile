FROM python:3.8.3-buster

ENV FLASK_ENV production

WORKDIR /opt/codeclusters-modeling

COPY server ./server
COPY run.py prod.sh app-requirements.txt ./

RUN pip install -r app-requirements.txt
RUN pip install psycopg2

CMD ["gunicorn", "-b", "localhost:8500", "run:app"]