import json
import backoff
import requests
import singer

LOGGER = singer.get_logger()

def call_api(catalog):
    headers = {'Content-type': 'application/json'}
    data = json.dumps(catalog)
    p = requests.post('https://api.bls.gov/publicAPI/v2/timeseries/data/', data=data, headers=headers)
    return json.loads(p.text)