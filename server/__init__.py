from flask import Flask
from flask_cors import CORS

import os

from server.routes import ngram_api
from server.routes import metrics_api
from server.services import db

def create_app(config=None, instance_path=None):
  app = Flask(__name__)
  app.register_blueprint(ngram_api.ngram, url_prefix='/ngram')
  app.register_blueprint(metrics_api.metrics, url_prefix='/metrics')
  db.init()
  cors = CORS(app, resources={r"*": {"origins": "*"}})
  return app
