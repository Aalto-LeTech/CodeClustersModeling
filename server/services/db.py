import psycopg2

import os

connection = None
cursor = None

def init():
  POSTGRES_HOST = os.getenv("DB_HOST")
  POSTGRES_PORT = os.getenv("DB_PORT")
  POSTGRES_DB = os.getenv("DB_NAME")
  POSTGRES_USER = os.getenv("DB_USER")
  POSTGRES_PASSWORD = os.getenv("DB_PASSWORD")

  conn = psycopg2.connect(host=POSTGRES_HOST, port=POSTGRES_PORT, database=POSTGRES_DB, user=POSTGRES_USER, password=POSTGRES_PASSWORD)

  global connection
  global cursor
  connection = conn
  cursor = conn.cursor()

def query_many(query):
  try:
    cursor.execute(query)
    return cursor.fetchall()
  except:
    cursor.execute("ROLLBACK")
    connection.commit()
    # If the database for some reason shuts down the database connection has to be recreated (it won't do it automatically)
    init()
    raise

def fetch_submissions(courseId, exerciseId):
  ex_rows = query_many(f"""
  SELECT programming_language FROM exercise WHERE course_id = {courseId} AND exercise_id = {exerciseId}
  """)
  rows = query_many(f"""
  SELECT submission_id, code FROM submission
  WHERE course_id = {courseId} AND exercise_id = {exerciseId}
  """)
  submissionIds = [r[0] for r in rows]
  codeList = [r[1] for r in rows]
  language = ex_rows[0][0]

  return submissionIds, codeList, language
