from flask import Flask
from flask_cors import CORS

import os

from server.routes import cluster_api
from server.routes import ngram_api
from server.services import db

def create_app(config=None, instance_path=None):
  app = Flask(__name__)
  app.register_blueprint(cluster_api.cluster, url_prefix='/cluster')
  app.register_blueprint(ngram_api.ngram, url_prefix='/ngram')
  db.init()
  cors = CORS(app, resources={r"*": {"origins": "*"}})
  return app
