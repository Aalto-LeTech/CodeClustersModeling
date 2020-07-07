import requests

SOLR_URL="http://localhost:8983"
CORE="submission-search"

def add_dynamic_field(fieldName, fieldType="pint"):
  url = f'{SOLR_URL}/solr/{CORE}/schema?commit=true'
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
  url = f'{SOLR_URL}/solr/{CORE}/update?overwrite=true&commit=true'
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
