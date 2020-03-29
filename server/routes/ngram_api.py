import traceback
import json

import numpy as np
from flask import current_app, request, jsonify, send_file, make_response, Blueprint
from server.services import clusterer

ngram = Blueprint('ngram', __name__)

@ngram.route('', methods=['POST'])
def run_ngram_model():
  body = request.get_json()
  if 'submission_ids' not in body:
    return 'submission_ids missing from JSON', 400
  try:
    clusters = clusterer.run_ngram(body)
    return json.dumps(clusters, cls=NumpyEncoder)
  except OSError as e:
    print(traceback.format_exc())
    return 'I am broken', 500

class NumpyEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, np.ndarray):
      return obj.tolist()
    return json.JSONEncoder.default(self, obj)
