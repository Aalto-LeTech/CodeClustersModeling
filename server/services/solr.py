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

def update_submission_metrics_and_keywords(metricsDict, keywordsDict, submissionIds):
  def create_solr_updation(subId):
    sub_metrics = metricsDict[subId]
    sub_keywords = keywordsDict[subId]['keywords']
    sub_rare_keywords = keywordsDict[subId]['rare_keywords']
    a = { f'{key}_metric': { "set": sub_metrics[key] } for key in sub_metrics.keys() }
    b = { f'{key}_keywords': { "set": sub_keywords[key] } for key in sub_keywords.keys() }
    c = { f'{key}_rare_keywords': { "set": sub_rare_keywords[key] } for key in sub_rare_keywords.keys() }
    res = { **a, **b, **c }
    res['id'] = subId
    return res

  url = create_url('update?overwrite=true&commit=true')
  data = [create_solr_updation(sub_id) for sub_id in submissionIds]
  headers = {
    "Content-type": "application/json"
  }
  resp = requests.post(url, json=data, headers=headers)

  return resp.json()
