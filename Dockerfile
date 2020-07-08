FROM frolvlad/alpine-miniconda3:python3.7

ENV FLASK_ENV production
ENV METRICS_FOLDER_PATH /tmp/codeclusters-run-metrics
ENV CHECKSTYLE_JAR_PATH /opt/codeclusters-modeling/tmp/checkstyle-8.34-all.jar
ENV CHECKSTYLE_XML_PATH /opt/codeclusters-modeling/metrics-checks.xml

WORKDIR /opt/codeclusters-modeling

RUN conda install -c conda-forge hdbscan

RUN apk update \
  && apk upgrade \
  && apk add --no-cache bash \
  && apk add --no-cache --virtual=build-dependencies unzip \
  && apk add --no-cache curl \
  && apk add --no-cache postgresql-dev \
  && apk add --no-cache openjdk8-jre

COPY app-requirements.txt ./
RUN pip install psycopg2-binary
RUN pip install -r app-requirements.txt

WORKDIR /opt/codeclusters-modeling/tmp
RUN curl -OL https://github.com/checkstyle/checkstyle/releases/download/checkstyle-8.34/checkstyle-8.34-all.jar
WORKDIR /opt/codeclusters-modeling

COPY server ./server
COPY run.py gunicorn-conf.py metrics/metrics-checks.xml ./

EXPOSE 8500

CMD ["gunicorn", "-c", "gunicorn-conf.py", "run:app"]