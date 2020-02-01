import psycopg2

import os

cur = None

def init():
  POSTGRES_HOST = os.getenv("DB_HOST")
  POSTGRES_PORT = os.getenv("DB_PORT")
  POSTGRES_DB = os.getenv("DB_NAME")
  POSTGRES_USER = os.getenv("DB_USER")
  POSTGRES_PASSWORD = os.getenv("DB_PASSWORD")

  conn = psycopg2.connect(host=POSTGRES_HOST, port=POSTGRES_PORT, database=POSTGRES_DB, user=POSTGRES_USER, password=POSTGRES_PASSWORD)

  global cur
  cur = conn.cursor()

def query_many(query):
  cur.execute(query)
  return cur.fetchall()
