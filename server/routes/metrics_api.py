import traceback
import json

import numpy as np
from flask import current_app, request, jsonify, send_file, make_response, Blueprint
from server.services.db import fetch_submissions
from server.services.solr import update_submission_metrics
from server.services.metrics import run_metrics

metrics = Blueprint('metrics', __name__)

@metrics.route('', methods=['POST'])
def run_and_index_metrics():
  body = request.get_json()
  if 'course_id' not in body:
    return 'course_id missing from JSON', 400
  if 'exercise_id' not in body:
    return 'exercise_id missing from JSON', 400
  try:
    courseId = body.get('course_id')
    exerciseId = body.get('exercise_id')
    submissionIds, codeLines, language = fetch_submissions(courseId, exerciseId)
    res = run_metrics(submissionIds, codeLines, language)
    resp = update_submission_metrics(res)
    return json.dumps(resp)
  except OSError as e:
    print(traceback.format_exc())
    return 'I am broken', 500
