import traceback

from flask import current_app, request, jsonify, send_file, make_response, Blueprint
from server.services import clusterer

cluster = Blueprint('cluster', __name__)

@cluster.route('', methods=['POST'])
def cluster_code():
  body = request.get_json()
  if 'course_id' not in body:
    return 'course_id missing from JSON', 400

  if 'exercise_id' not in body:
    return 'exercise_id missing from JSON', 400

  try:
    clusters = clusterer.cluster_submissions(body['course_id'], body['exercise_id'],)

    return jsonify({
      "clusters": clusters
    })
  except OSError as e:
    print(traceback.format_exc())
    return 'I am broken', 500
