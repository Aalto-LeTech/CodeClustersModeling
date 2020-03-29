from server.services import db
from server.services.ngram import ngram

def run_ngram(params):
  submission_ids = params.get('submission_ids')
  ngrams = params.get('ngrams')
  n_components = params.get('n_components') or 50
  word_filters = params.get('word_filters')
  rows = db.query_many(f"""
SELECT submission_id, code FROM submission WHERE submission_id = ANY(array{submission_ids}::uuid[])
""")
  codeList = [r[1] for r in rows]
  # print(codeList)
  ngram_result = ngram.run_ngram(codeList, ngrams, n_components)
  if word_filters and len(word_filters) > 0:
    filter_result = ngram.group_by_strings(dict(rows), word_filters)
  else:
    filter_result = {}
  return {
    "ngram": ngram_result,
    "filter": filter_result
  }

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
