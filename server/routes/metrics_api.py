import traceback
import json

import numpy as np
from flask import current_app, request, jsonify, send_file, make_response, Blueprint
from server.services.db import fetch_submissions
from server.services.solr import update_submission_metrics_and_keywords
from server.services.metrics import run_metrics
from server.services.keywords import parse_keywords

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
    metricsDict = run_metrics(submissionIds, codeLines, language)
    keywordsDict = parse_keywords(submissionIds, codeLines)
    resp = update_submission_metrics_and_keywords(metricsDict, keywordsDict, submissionIds)
    return json.dumps(resp)
  except OSError as e:
    print(traceback.format_exc())
    return 'Internal server error', 500
