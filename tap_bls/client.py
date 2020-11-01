#!/usr/bin/env python3

import json
import backoff
import requests

def log_the_api_call_to_file(p):
    with open("api_call.txt", "a") as f:
        f.write(str(json.loads(p.text))+"\n")

def call_api(catalog):
    headers = {'Content-type': 'application/json'}
    data = json.dumps(catalog)
    p = requests.post('https://api.bls.gov/publicAPI/v2/timeseries/data/', data=data, headers=headers)
    
    log_the_api_call_to_file(p)
    
    return json.loads(p.text)