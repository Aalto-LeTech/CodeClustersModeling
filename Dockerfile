FROM python:3.10.5-buster

WORKDIR /opt/codeclusters-modeling

RUN apt-get update \
  && apt-get -y install postgresql \
  && apt-get -y install openjdk-11-jdk

COPY requirements.txt ./
RUN pip install --upgrade pip
# Basically pip install \
#   numpy pandas scipy scikit-learn Cython hdbscan umap umap-learn requests antlr4-python3-runtime \
#   psycopg2-binary gunicorn python-dotenv Flask Flask-Cors matplotlib ipython jupyter pandas sympy nose
RUN pip install -r requirements.txt

WORKDIR /opt/codeclusters-modeling/lib
RUN curl -OL https://github.com/checkstyle/checkstyle/releases/download/checkstyle-10.3.2/checkstyle-10.3.2-all.jar
WORKDIR /opt/codeclusters-modeling

COPY server ./server
COPY run.py gunicorn-conf.py metrics/metrics-checks.xml ./

EXPOSE 8500

ENV FLASK_ENV production
ENV METRICS_FOLDER_PATH /tmp/codeclusters-run-metrics
ENV CHECKSTYLE_JAR_PATH /opt/codeclusters-modeling/lib/checkstyle-10.3.2-all.jar
ENV CHECKSTYLE_XML_PATH /opt/codeclusters-modeling/metrics-checks.xml

CMD ["gunicorn", "-c", "gunicorn-conf.py", "run:app"]