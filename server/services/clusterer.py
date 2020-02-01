from server.services import db

def cluster_submission(result):
  return {
    'submission_id': result[0],
    'cluster': len(result[1])%2
  }

def cluster_submissions(courseId, exerciseId):
  result = db.query_many(f"""SELECT id AS submission_id, code FROM submission WHERE course_id = {courseId} AND exercise_id = {exerciseId}""")
  return [cluster_submission(r) for r in result]
