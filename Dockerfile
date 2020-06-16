FROM python:3.8.3-buster

ENV FLASK_ENV production

WORKDIR /opt/codeclusters-modeling

COPY app-requirements.txt ./
RUN pip install -r app-requirements.txt
RUN pip install psycopg2

COPY server ./server
COPY run.py gunicorn-conf.py ./

EXPOSE 8500

CMD ["gunicorn", "-c", "gunicorn-conf.py", "run:app"]