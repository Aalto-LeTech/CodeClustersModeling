import traceback
import json

import numpy as np
from flask import current_app, request, jsonify, send_file, make_response, Blueprint
from server.services.metrics import create_metrics

metrics = Blueprint('metrics', __name__)

@metrics.route('', methods=['POST'])
def run_metrics():
  body = request.get_json()
  if 'submissions' not in body:
    return 'submissions missing from JSON', 400
  try:
    metrics = create_metrics(body)
    return json.dumps(metrics)
  except OSError as e:
    print(traceback.format_exc())
    return 'I am broken', 500

# class NumpyEncoder(json.JSONEncoder):
#   def default(self, obj):
#     if isinstance(obj, np.ndarray):
#       return obj.tolist()
#     elif isinstance(obj, np.float32):
#       return np.round(obj.item(), 3)
#     return json.JSONEncoder.default(self, obj)
