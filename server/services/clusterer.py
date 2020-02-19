from server.services import db
from server.services.ngram import ngram

def cluster_submissions(courseId, exerciseId, wordFilters):
  rows = db.query_many(f"""SELECT id AS submission_id, code FROM submission WHERE course_id = {courseId} AND exercise_id = {exerciseId}""")
  codeList = [r[1] for r in rows]
  # print(codeList)
  ngram_result = ngram.run_ngram(codeList)
  if len(wordFilters) > 0:
    filter_result = ngram.group_by_strings(dict(rows), wordFilters)
  else:
    filter_result = {}
  return {
    "ngram": ngram_result,
    "filter": filter_result
  }
