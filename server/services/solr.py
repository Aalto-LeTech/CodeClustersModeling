import os
import requests

def create_url(path):
  SOLR_URL = os.getenv("SOLR_URL")
  SOLR_CORE = os.getenv("SOLR_CORE")
  return f'{SOLR_URL}/solr/{SOLR_CORE}/{path}'

def add_dynamic_field(fieldName, fieldType="pint"):
  url = create_url('schema?commit=true')
  data = {
    "add-dynamic-field": {
      "stored": "true",
      "indexed": "true",
      "name": f'*_{fieldName}',
      "type": fieldType
    }
  }
  headers = {
    "Content-type": "application/json"
  }
  res = requests.post(url, json=data, headers=headers)
  print(res.text)
  return res

def update_submission_metrics(res):
  url = create_url('update?overwrite=true&commit=true')
  print(url)
  def create_solr_updation(d, subId):
    r = { f'{key}_metric': { "set": d[key] } for key in d.keys() }
    r['id'] = subId
    return r
  data = [create_solr_updation(res[sub_id], sub_id) for sub_id in res.keys()]
  headers = {
    "Content-type": "application/json"
  }
  resp = requests.post(url, json=data, headers=headers)
  print(resp.text)
  return resp.json()
