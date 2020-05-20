import traceback
import json

import numpy as np
from flask import current_app, request, jsonify, send_file, make_response, Blueprint
from server.services.ngram import run_ngram

ngram = Blueprint('ngram', __name__)

@ngram.route('', methods=['POST'])
def run_ngram_model():
  body = request.get_json()
  if 'submissions' not in body:
    return 'submissions missing from JSON', 400
  try:
    submissions = body.get('submissions')
    token_set = body.get('token_set')
    ngrams = body.get('ngrams')
    random_seed = body.get('random_seed')
    clustering_params = body.get('clustering_params')
    dim_visualization_params = body.get('dim_visualization_params')

    submissionIds = [s['id'] for s in submissions]
    codeList = [s['code'] for s in submissions]

    ngram_result = run_ngram(submissionIds, codeList, token_set, ngrams, random_seed,
      clustering_params, dim_visualization_params)
    response = {
      "ngram": ngram_result
    }
    return json.dumps(response, cls=NumpyEncoder)
  except OSError as e:
    print(traceback.format_exc())
    return 'I am broken', 500

class NumpyEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, np.ndarray):
      return obj.tolist()
    elif isinstance(obj, np.float32):
      return np.round(obj.item(), 3)
    return json.JSONEncoder.default(self, obj)
